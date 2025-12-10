from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import asyncio
import requests
import json
import pandas as pd
from io import StringIO

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Neo4j connection
neo4j_uri = os.environ['NEO4J_URI']
neo4j_user = os.environ['NEO4J_USERNAME']
neo4j_password = os.environ['NEO4J_PASSWORD']
neo4j_database = os.environ['NEO4J_DATABASE']

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# LLM API Configuration
gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
openai_api_key = os.environ.get('OPENAI_API_KEY', '')

if not gemini_api_key and not openai_api_key:
    logging.warning("No LLM API key set. LLM features will be limited.")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    cypher_query: str
    results: List[Dict[str, Any]]

class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]

class SeedDataRequest(BaseModel):
    clear_existing: bool = False
    region: str = None  # 'BR', 'full', or None for sample

# Helper function to run Neo4j queries
def run_neo4j_query(query: str, parameters: dict = None):
    def serialize_neo4j_object(obj):
        """Convert Neo4j objects to serializable dictionaries"""
        if hasattr(obj, '_properties'):  # Neo4j Node or Relationship
            return dict(obj._properties)
        elif hasattr(obj, 'items'):  # Dictionary-like
            return {k: serialize_neo4j_object(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_neo4j_object(item) for item in obj]
        else:
            return obj
    
    with driver.session(database=neo4j_database) as session:
        result = session.run(query, parameters or {})
        records = []
        for record in result:
            record_dict = {}
            for key, value in record.items():
                record_dict[key] = serialize_neo4j_object(value)
            records.append(record_dict)
        return records

# Helper function to call OpenAI API
def call_openai_api(prompt: str) -> str:
    """Call OpenAI API"""
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 300
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result["choices"][0]["message"]["content"]

# Helper function to list available Gemini models
def list_available_models():
    """List all available Gemini models"""
    if not gemini_api_key:
        return []
    
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    params = {"key": gemini_api_key}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Get models that support generateContent
            valid_models = [
                m["name"].replace("models/", "") 
                for m in models 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            logging.info(f"Available Gemini models: {valid_models}")
            return valid_models
        else:
            logging.warning(f"Failed to list models: {response.status_code}")
            return []
    except Exception as e:
        logging.warning(f"Error listing models: {e}")
        return []

# Helper function to call Gemini API directly via REST
def call_gemini_api(prompt: str, model_name: str) -> str:
    """Call Google Gemini API directly using REST"""
    # Don't add models/ prefix - API expects just the model name
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 512
        }
    }
    
    params = {
        "key": gemini_api_key
    }
    
    response = requests.post(url, headers=headers, params=params, json=payload, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

# Cache the working model
_working_model = None

# Helper function to generate Cypher query using LLM
async def generate_cypher_query(natural_language_query: str) -> str:
    """Generate a Cypher query from natural language using LLM"""
    global _working_model
    
    if not openai_api_key and not gemini_api_key:
        raise HTTPException(status_code=500, detail="No LLM API key configured")
    
    system_prompt = """Neo4j Cypher expert. Aviation database with:
- Airport: code, name, city, country
- Airline: code, name, country
- ROUTE: airline, distance_km, duration_hours

Return ONLY Cypher query. LIMIT 50.

Examples:
- "airports in Brazil" -> MATCH (a:Airport {country: 'Brazil'}) RETURN a LIMIT 50
- "routes from GRU" -> MATCH (a:Airport {code: 'GRU'})-[r:ROUTE]->(b:Airport) RETURN a, r, b LIMIT 50
"""
    
    full_prompt = f"{system_prompt}\n\nQuestion: {natural_language_query}"
    
    # Try OpenAI first (more reliable)
    if openai_api_key:
        try:
            logging.info("Using OpenAI API")
            response_text = call_openai_api(full_prompt)
            
            cypher_query = response_text.strip()
            
            # Remove markdown code blocks if present
            if cypher_query.startswith('```'):
                lines = cypher_query.split('\n')
                cypher_query = '\n'.join(lines[1:-1] if len(lines) > 2 and lines[-1].strip() == '```' else lines[1:])
            
            return cypher_query.strip()
        except Exception as e:
            logging.warning(f"OpenAI failed: {e}. Trying Gemini...")
    
    # Fallback to Gemini
    if gemini_api_key:
        # Get available models if not cached
        if _working_model is None:
            available_models = list_available_models()
            if not available_models:
                raise HTTPException(status_code=500, detail="No models available")
            _working_model = available_models[0]
            logging.info(f"Selected Gemini model: {_working_model}")
        
        try:
            logging.info(f"Using Gemini model: {_working_model}")
            response_text = call_gemini_api(full_prompt, _working_model)
            
            cypher_query = response_text.strip()
            
            # Remove markdown code blocks if present
            if cypher_query.startswith('```'):
                lines = cypher_query.split('\n')
                cypher_query = '\n'.join(lines[1:-1] if len(lines) > 2 and lines[-1].strip() == '```' else lines[1:])
            
            return cypher_query.strip()
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Gemini failed: {error_msg}")
            _working_model = None
            raise HTTPException(status_code=500, detail=f"Failed to generate query: {error_msg}")
    
    raise HTTPException(status_code=500, detail="All LLM providers failed")

@api_router.get("/")
async def root():
    return {"message": "AeroGraph Analytics API - GraphRAG with Neo4j"}

@api_router.post("/graphrag/query", response_model=QueryResponse)
async def graphrag_query(request: QueryRequest):
    try:
        # Generate Cypher query using LLM with timeout
        cypher_query = await asyncio.wait_for(
            generate_cypher_query(request.query),
            timeout=15.0  # 15 second timeout for query generation
        )
        
        # Execute the generated query
        results = run_neo4j_query(cypher_query)
        
        # Generate natural language answer using LLM
        if openai_api_key or gemini_api_key:
            try:
                answer_prompt = f"""Query: {request.query}
Results (first 3): {results[:3]}

Answer in Portuguese, 2 sentences max."""
                
                # Try OpenAI first
                if openai_api_key:
                    try:
                        answer = call_openai_api(answer_prompt)
                    except:
                        if gemini_api_key and _working_model:
                            answer = call_gemini_api(answer_prompt, _working_model)
                        else:
                            raise
                else:
                    answer = call_gemini_api(answer_prompt, _working_model)
            except Exception as e:
                logging.warning(f"Could not generate answer with LLM: {str(e)}. Using basic response.")
                answer = f"Found {len(results)} results for your query."
        else:
            answer = f"Found {len(results)} results for your query."
        
        return QueryResponse(
            answer=answer,
            cypher_query=cypher_query,
            results=results[:50]
        )
    except asyncio.TimeoutError:
        logging.error(f"Query timed out after 15 seconds")
        raise HTTPException(status_code=504, detail="Query timed out. Please try a simpler question.")
    except Exception as e:
        logging.error(f"Error in graphrag_query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@api_router.post("/query")
async def direct_cypher_query(request: QueryRequest):
    """Execute a direct Cypher query without AI processing (for preset buttons)"""
    try:
        # Execute the Cypher query directly
        results = run_neo4j_query(request.query)
        
        # Filter out null and 'Unknown' values from results
        filtered_results = []
        for result in results[:50]:
            filtered_result = {}
            for key, value in result.items():
                if isinstance(value, dict):
                    # Filter nested properties
                    filtered_nested = {k: v for k, v in value.items() 
                                     if v is not None and v != '' and str(v).lower() not in ['unknown', 'null', 'none']}
                    if filtered_nested:
                        filtered_result[key] = filtered_nested
                elif value is not None and value != '' and str(value).lower() not in ['unknown', 'null', 'none']:
                    filtered_result[key] = value
            if filtered_result:
                filtered_results.append(filtered_result)
        
        return {
            "answer": f"Consulta executada com sucesso. {len(filtered_results)} resultados encontrados.",
            "cypher_query": request.query,
            "results": filtered_results
        }
    except Exception as e:
        logging.error(f"Error in direct query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@api_router.get("/graph/data", response_model=GraphData)
async def get_graph_data():
    try:
        # Get nodes (airports and airlines) - no limit to show all data
        nodes_query = """
        MATCH (n)
        WHERE n:Airport OR n:Airline
        RETURN id(n) as id, labels(n)[0] as label, properties(n) as properties
        """
        nodes_data = run_neo4j_query(nodes_query)
        
        # Get relationships - no limit to show all data
        links_query = """
        MATCH (a)-[r:ROUTE]->(b)
        RETURN id(a) as source, id(b) as target, type(r) as type, properties(r) as properties
        """
        links_data = run_neo4j_query(links_query)
        
        # Format nodes
        nodes = []
        for node in nodes_data:
            node_id = node['id']
            label = node['label']
            props = node['properties']
            
            # Filter out null and 'Unknown' values
            filtered_props = {}
            for key, value in props.items():
                if value is not None and value != '' and str(value).lower() not in ['unknown', 'null', 'none']:
                    filtered_props[key] = value
            
            nodes.append({
                'id': str(node_id),
                'label': label,
                'name': filtered_props.get('name') or filtered_props.get('code', f"{label}_{node_id}"),
                'properties': filtered_props
            })
        
        # Format links
        links = []
        for link in links_data:
            links.append({
                'source': str(link['source']),
                'target': str(link['target']),
                'type': link['type'],
                'properties': link.get('properties', {})
            })
        
        return GraphData(nodes=nodes, links=links)
    except Exception as e:
        logging.error(f"Error getting graph data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving graph data: {str(e)}")

@api_router.get("/examples")
async def get_example_queries():
    return [
        {
            "id": 1,
            "question": "Quais aeroportos estão no Brasil?",
            "description": "Lista todos os aeroportos brasileiros"
        },
        {
            "id": 2,
            "question": "Mostre todas as rotas saindo de GRU",
            "description": "Rotas do Aeroporto de Guarulhos"
        },
        {
            "id": 3,
            "question": "Quais companhias aéreas operam rotas internacionais?",
            "description": "Companhias com rotas entre países"
        },
        {
            "id": 4,
            "question": "Qual é a rota mais longa?",
            "description": "Rota com maior distância"
        },
        {
            "id": 5,
            "question": "Quantos aeroportos existem em cada país?",
            "description": "Contagem de aeroportos por país"
        }
    ]

@api_router.post("/seed-data")
async def seed_data(request: SeedDataRequest):
    """
    Seed database with data
    - region=None: Sample data (10 airports)
    - region='BR': All Brazil-related data
    - region='full': Complete dataset (3993 nodes)
    """
    try:
        # Clear existing data if requested
        if request.clear_existing:
            run_neo4j_query("MATCH (n) DETACH DELETE n")
        
        if request.region == 'BR':
            # Load all Brazil-related airports and their connections
            return await seed_brazil_data()
        elif request.region == 'full':
            # Load complete dataset
            return await seed_full_dataset()
        else:
            # Load sample data (original 10 airports)
            return await seed_sample_data()
            
    except Exception as e:
        logging.error(f"Error seeding data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")

async def seed_sample_data():
    """Load sample data with 10 airports"""
    # Create airports
    airports = [
        {"code": "GRU", "name": "Aeroporto Internacional de São Paulo/Guarulhos", "city": "São Paulo", "country": "Brazil"},
        {"code": "CGH", "name": "Aeroporto de Congonhas", "city": "São Paulo", "country": "Brazil"},
        {"code": "GIG", "name": "Aeroporto Internacional do Rio de Janeiro/Galeão", "city": "Rio de Janeiro", "country": "Brazil"},
        {"code": "BSB", "name": "Aeroporto Internacional de Brasília", "city": "Brasília", "country": "Brazil"},
        {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA"},
        {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA"},
        {"code": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "UK"},
        {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
        {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
        {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE"}
    ]
    
    for airport in airports:
        query = """
        MERGE (a:Airport {code: $code})
        SET a.name = $name, a.city = $city, a.country = $country
        """
        run_neo4j_query(query, airport)
    
    # Create airlines
    airlines = [
        {"code": "LATAM", "name": "LATAM Airlines", "country": "Brazil"},
        {"code": "GOL", "name": "Gol Linhas Aéreas", "country": "Brazil"},
        {"code": "AA", "name": "American Airlines", "country": "USA"},
        {"code": "BA", "name": "British Airways", "country": "UK"},
        {"code": "EK", "name": "Emirates", "country": "UAE"}
    ]
    
    for airline in airlines:
        query = """
        MERGE (al:Airline {code: $code})
        SET al.name = $name, al.country = $country
        """
        run_neo4j_query(query, airline)
    
    # Create routes
    routes = [
        {"from": "GRU", "to": "GIG", "airline": "LATAM", "distance": 365, "duration": 1.0},
        {"from": "GRU", "to": "BSB", "airline": "GOL", "distance": 872, "duration": 1.5},
        {"from": "GRU", "to": "JFK", "airline": "LATAM", "distance": 7680, "duration": 10.5},
        {"from": "GIG", "to": "JFK", "airline": "AA", "distance": 7750, "duration": 10.0},
        {"from": "GRU", "to": "LHR", "airline": "BA", "distance": 9450, "duration": 11.5},
        {"from": "JFK", "to": "LAX", "airline": "AA", "distance": 3970, "duration": 5.5},
        {"from": "LHR", "to": "CDG", "airline": "BA", "distance": 340, "duration": 1.0},
        {"from": "DXB", "to": "LHR", "airline": "EK", "distance": 5470, "duration": 7.0},
        {"from": "NRT", "to": "LAX", "airline": "AA", "distance": 8800, "duration": 11.0},
        {"from": "CGH", "to": "GIG", "airline": "GOL", "distance": 365, "duration": 1.0}
    ]
    
    for route in routes:
        query = """
        MATCH (a:Airport)
        WHERE a.code = $from
        MATCH (b:Airport)
        WHERE b.code = $to
        MERGE (a)-[r:ROUTE {airline: $airline}]->(b)
        SET r.distance_km = $distance, r.duration_hours = $duration
        """
        run_neo4j_query(query, route)
    
    return {"message": "Sample data loaded", "airports": len(airports), "airlines": len(airlines), "routes": len(routes)}

async def seed_brazil_data():
    """Load all Brazil-related airports and routes"""
    try:
        logging.info("Loading Brazil dataset...")
        
        # Load airports from global dataset, filter by Brazil
        url_airports = 'https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv'
        airports_df = pd.read_csv(url_airports)
        
        # Filter Brazilian airports
        br_airports = airports_df[airports_df['iso_country'] == 'BR'].copy()
        
        # Create airports
        airport_count = 0
        for _, row in br_airports.iterrows():
            if pd.notna(row.get('iata_code')) and row.get('iata_code'):
                query = """
                MERGE (a:Airport {code: $code})
                SET a.name = $name, 
                    a.city = $city, 
                    a.country = 'Brazil',
                    a.latitude = $latitude,
                    a.longitude = $longitude
                """
                params = {
                    'code': row['iata_code'],
                    'name': row.get('name', ''),
                    'city': row.get('municipality', ''),
                    'latitude': float(row['coordinates'].split(',')[1]) if pd.notna(row.get('coordinates')) else 0.0,
                    'longitude': float(row['coordinates'].split(',')[0]) if pd.notna(row.get('coordinates')) else 0.0
                }
                run_neo4j_query(query, params)
                airport_count += 1
        
        # Load routes involving Brazilian airports
        url_routes = 'https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/13e519574832172b538fd5588673132cb826cd20/routes.csv'
        routes_df = pd.read_csv(url_routes)
        
        # Get list of Brazilian airport codes
        br_codes = set(br_airports['iata_code'].dropna().values)
        
        # Filter routes where source OR destination is in Brazil
        # Note: CSV has typo 'destination_apirport' instead of 'destination_airport'
        br_routes = routes_df[
            (routes_df['source_airport'].isin(br_codes)) | 
            (routes_df['destination_apirport'].isin(br_codes))
        ].copy()
        
        route_count = 0
        for _, route in br_routes.iterrows():
            try:
                airline = route.get('airline', '')
                
                # Skip if airline is Unknown or empty
                if not airline or str(airline).lower() in ['unknown', 'null', 'none']:
                    continue
                
                query = """
                MATCH (a:Airport)
                WHERE a.code = $from
                MATCH (b:Airport)
                WHERE b.code = $to
                MERGE (a)-[r:ROUTE {airline: $airline}]->(b)
                SET r.distance_km = $distance
                """
                params = {
                    'from': route['source_airport'],
                    'to': route['destination_apirport'],
                    'airline': airline,
                    'distance': float(route.get('distance', 0))
                }
                run_neo4j_query(query, params)
                route_count += 1
            except Exception as e:
                continue
        
        # Load Brazilian airlines - BATCH OPTIMIZED
        url_airlines = 'https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/2697297ee7ae3eed7c679f7d1f195c1f502aa11b/Airlines_Unicas.csv'
        airlines_df = pd.read_csv(url_airlines)
        
        # Prepare batch - extract code, name, country
        def get_code(row):
            return row.get('IATA') or row.get('ICAO') or row.get('Code') or 'Unknown'
        
        def get_name(row):
            return row.get('Name') or row.get('Airline') or 'Unknown'
        
        airlines_df['code'] = airlines_df.apply(get_code, axis=1)
        airlines_df['name'] = airlines_df.apply(get_name, axis=1)
        airlines_df['country'] = airlines_df['Country'].fillna('Brazil') if 'Country' in airlines_df.columns else 'Brazil'
        
        airlines_batch = airlines_df[['code', 'name', 'country']].to_dict('records')
        
        # Batch insert airlines
        airline_count = 0
        if airlines_batch:
            query = """
            UNWIND $batch as airline
            MERGE (al:Airline {code: airline.code})
            SET al.name = airline.name, al.country = airline.country
            """
            run_neo4j_query(query, {'batch': airlines_batch})
            airline_count = len(airlines_batch)
        
        logging.info(f"Brazil data loaded: {airport_count} airports, {airline_count} airlines, {route_count} routes")
        return {
            "message": "Brazil data loaded successfully", 
            "airports": airport_count,
            "airlines": airline_count,
            "routes": route_count
        }
    except Exception as e:
        logging.error(f"Error loading Brazil data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading Brazil data: {str(e)}")

async def seed_full_dataset():
    """Load complete dataset with all airports and routes - OPTIMIZED"""
    try:
        # Force rebuild: 2025-12-10 22:08 UTC
        logging.info("Loading full dataset with batch processing...")
        
        # Load airports - optimized with vectorized operations
        url_airports = 'https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv'
        airports_df = pd.read_csv(url_airports)
        
        logging.info(f"Processing {len(airports_df)} airport rows from CSV...")
        
        # Filter for valid IATA codes using vectorized operations
        airports_df = airports_df[airports_df['iata_code'].notna()].copy()
        airports_df['iata_code'] = airports_df['iata_code'].str.strip().str.upper()
        airports_df = airports_df[airports_df['iata_code'].str.len() == 3]
        airports_df = airports_df[airports_df['iata_code'].str.isalpha()]
        
        # Parse coordinates vectorized
        airports_df[['lon', 'lat']] = airports_df['coordinates'].str.split(',', expand=True).astype(float, errors='ignore').fillna(0.0)
        
        # Prepare batch data
        airports_batch = airports_df[['iata_code', 'name', 'municipality', 'iso_country', 'lat', 'lon']].rename(
            columns={'iata_code': 'code', 'municipality': 'city', 'iso_country': 'country', 'lat': 'latitude', 'lon': 'longitude'}
        ).fillna('').to_dict('records')
        
        logging.info(f"Filtered to {len(airports_batch)} airports with valid IATA codes")
        
        # Batch insert all airports at once
        if airports_batch:
            query = """
            UNWIND $batch as airport
            MERGE (a:Airport {code: airport.code})
            SET a.name = airport.name, 
                a.city = airport.city, 
                a.country = airport.country,
                a.latitude = airport.latitude,
                a.longitude = airport.longitude
            """
            run_neo4j_query(query, {'batch': airports_batch})
            airport_count = len(airports_batch)
            logging.info(f"Loaded {airport_count} airports in batch")
        else:
            airport_count = 0
        
        # Load ALL routes - optimized
        logging.info("Loading routes from CSV...")
        url_routes = 'https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/13e519574832172b538fd5588673132cb826cd20/routes.csv'
        routes_df = pd.read_csv(url_routes)
        logging.info(f"Read {len(routes_df)} routes from CSV")
        
        # Prepare batch data with vectorized operations
        routes_df['airline'] = routes_df['airline'].fillna('Unknown')
        routes_df['distance'] = pd.to_numeric(routes_df['distance'], errors='coerce').fillna(0.0)
        
        routes_batch = routes_df[['source_airport', 'destination_apirport', 'airline', 'distance']].rename(
            columns={'source_airport': 'from', 'destination_apirport': 'to'}
        ).to_dict('records')
        
        # Batch insert routes
        route_count = 0
        if routes_batch:
            query = """
            UNWIND $batch as route
            MATCH (a:Airport)
            WHERE a.code = route.from
            MATCH (b:Airport)
            WHERE b.code = route.to
            MERGE (a)-[r:ROUTE {airline: route.airline}]->(b)
            SET r.distance_km = route.distance
            """
            run_neo4j_query(query, {'batch': routes_batch})
            route_count = len(routes_batch)
            logging.info(f"Loaded {route_count} routes in batch")
        
        # Load ALL airlines - optimized
        logging.info("Loading airlines from CSV...")
        url_base_airlines = 'https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/2697297ee7ae3eed7c679f7d1f195c1f502aa11b/Airlines_Unicas.csv'
        url_info_airlines = 'https://gist.githubusercontent.com/XimenesJu/23ff54741a6f183b2c7e367d003dcc69/raw/2697297ee7ae3eed7c679f7d1f195c1f502aa11b/airline_info.csv'
        
        airlines_base_df = pd.read_csv(url_base_airlines)
        airlines_info_df = pd.read_csv(url_info_airlines)
        
        # Merge and deduplicate
        airlines_df = pd.concat([airlines_base_df, airlines_info_df], ignore_index=True).drop_duplicates()
        logging.info(f"Merged {len(airlines_df)} unique airlines from both sources")
        
        # Combine code columns
        airlines_df['code'] = airlines_df.get('IATA', airlines_df.get('ICAO', airlines_df.get('Code', ''))).fillna('Unknown')
        airlines_df['name'] = airlines_df.get('Name', airlines_df.get('Airline', '')).fillna('Unknown')
        airlines_df['country'] = airlines_df.get('Country', '').fillna('')
        
        # Filter out completely empty rows
        airlines_df = airlines_df[(airlines_df['code'] != '') | (airlines_df['name'] != '')]
        airlines_df['code'] = airlines_df['code'].replace('', 'Unknown')
        airlines_df['name'] = airlines_df['name'].replace('', 'Unknown')
        
        # Prepare batch
        airlines_batch = airlines_df[['code', 'name', 'country']].to_dict('records')
        
        # Batch insert airlines
        airline_count = 0
        if airlines_batch:
            query = """
            UNWIND $batch as airline
            MERGE (al:Airline {code: airline.code})
            SET al.name = airline.name
            SET al.country = CASE WHEN airline.country IS NOT NULL THEN airline.country ELSE al.country END
            """
            run_neo4j_query(query, {'batch': airlines_batch})
            airline_count = len(airlines_batch)
            logging.info(f"Loaded {airline_count} airlines in batch")
        
        logging.info(f"Full dataset loaded: {airport_count} airports, {airline_count} airlines, {route_count} routes")
        return {
            "message": "Full dataset loaded successfully",
            "airports": airport_count,
            "airlines": airline_count,
            "routes": route_count
        }
    except Exception as e:
        logging.error(f"Error loading full dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading full dataset: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_event():
    driver.close()