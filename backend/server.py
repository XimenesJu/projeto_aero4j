from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
import google.generativeai as genai
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Neo4j connection
neo4j_uri = os.environ['NEO4J_URI']
neo4j_user = os.environ['NEO4J_USERNAME']
neo4j_password = os.environ['NEO4J_PASSWORD']
neo4j_database = os.environ['NEO4J_DATABASE']

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Google Generative AI Configuration
gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    logging.warning("GEMINI_API_KEY not set. LLM features will be limited.")

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

# Helper function to generate Cypher query using LLM
async def generate_cypher_query(natural_language_query: str) -> str:
    """Generate a Cypher query from natural language using Google Gemini"""
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    system_prompt = """You are a Neo4j Cypher query expert. Given a natural language question about an aviation network database, 
generate a valid Cypher query. The database contains:

- Airport nodes with properties: code, name, city, country
- Airline nodes with properties: code, name, country
- ROUTE relationships connecting airports with properties: airline, distance_km, duration_hours

Return ONLY the Cypher query, no explanations. Use MATCH and RETURN statements.
Always limit results to 50 items maximum.

Examples:
- "Which airports are in Brazil?" -> MATCH (a:Airport {country: 'Brazil'}) RETURN a LIMIT 50
- "Show all routes from GRU" -> MATCH (a:Airport {code: 'GRU'})-[r:ROUTE]->(b:Airport) RETURN a, r, b LIMIT 50
- "Which airlines operate international routes?" -> MATCH (al:Airline)-[:OPERATES]->(a:Airport)-[r:ROUTE]->(b:Airport) WHERE a.country <> b.country RETURN DISTINCT al LIMIT 50
"""
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-001')
        response = model.generate_content(
            f"{system_prompt}\n\nQuestion: {natural_language_query}",
            generation_config=genai.types.GenerationConfig(temperature=0)
        )
        
        cypher_query = response.text.strip()
        
        # Remove markdown code blocks if present
        if cypher_query.startswith('```'):
            lines = cypher_query.split('\n')
            cypher_query = '\n'.join(lines[1:-1] if len(lines) > 2 and lines[-1].strip() == '```' else lines[1:])
        
        return cypher_query.strip()
    except Exception as e:
        logging.error(f"Error generating Cypher query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate query: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "AeroGraph Analytics API - GraphRAG with Neo4j"}

@api_router.post("/graphrag/query", response_model=QueryResponse)
async def graphrag_query(request: QueryRequest):
    try:
        # Generate Cypher query using LLM
        cypher_query = await generate_cypher_query(request.query)
        
        # Execute the generated query
        results = run_neo4j_query(cypher_query)
        
        # Generate natural language answer using Gemini
        if gemini_api_key:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-001')
                answer_prompt = f"""You are a helpful assistant that explains query results from an aviation network database.
                
Query: {request.query}
Results (first 5): {results[:5]}

Provide a clear, concise answer in Portuguese (Brazilian). Keep it under 3 sentences."""
                
                answer_response = model.generate_content(answer_prompt)
                answer = answer_response.text
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
    except Exception as e:
        logging.error(f"Error in graphrag_query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@api_router.get("/graph/data", response_model=GraphData)
async def get_graph_data():
    try:
        # Get nodes (airports and airlines)
        nodes_query = """
        MATCH (n)
        WHERE n:Airport OR n:Airline
        RETURN id(n) as id, labels(n)[0] as label, properties(n) as properties
        LIMIT 100
        """
        nodes_data = run_neo4j_query(nodes_query)
        
        # Get relationships
        links_query = """
        MATCH (a)-[r:ROUTE]->(b)
        RETURN id(a) as source, id(b) as target, type(r) as type, properties(r) as properties
        LIMIT 200
        """
        links_data = run_neo4j_query(links_query)
        
        # Format nodes
        nodes = []
        for node in nodes_data:
            node_id = node['id']
            label = node['label']
            props = node['properties']
            nodes.append({
                'id': str(node_id),
                'label': label,
                'name': props.get('name') or props.get('code', f"{label}_{node_id}"),
                'properties': props
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
    try:
        # Clear existing data if requested
        if request.clear_existing:
            run_neo4j_query("MATCH (n) DETACH DELETE n")
        
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
            CREATE (a:Airport {code: $code, name: $name, city: $city, country: $country})
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
            CREATE (al:Airline {code: $code, name: $name, country: $country})
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
            MATCH (a:Airport {code: $from}), (b:Airport {code: $to})
            CREATE (a)-[:ROUTE {airline: $airline, distance_km: $distance, duration_hours: $duration}]->(b)
            """
            run_neo4j_query(query, route)
        
        return {"message": "Data seeded successfully", "airports": len(airports), "airlines": len(airlines), "routes": len(routes)}
    except Exception as e:
        logging.error(f"Error seeding data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")

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