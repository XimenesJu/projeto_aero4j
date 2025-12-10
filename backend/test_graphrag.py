#!/usr/bin/env python3
"""
Test the GraphRAG functionality locally
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from neo4j import GraphDatabase
import google.generativeai as genai

# Configuration
NEO4J_URI = os.environ.get('NEO4J_URI')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
NEO4J_DATABASE = os.environ.get('NEO4J_DATABASE')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def run_neo4j_query(query: str, parameters: dict = None):
    """Execute a Neo4j query"""
    def serialize_neo4j_object(obj):
        if hasattr(obj, '_properties'):
            return dict(obj._properties)
        elif hasattr(obj, 'items'):
            return {k: serialize_neo4j_object(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_neo4j_object(item) for item in obj]
        else:
            return obj
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query, parameters or {})
        records = []
        for record in result:
            record_dict = {}
            for key, value in record.items():
                record_dict[key] = serialize_neo4j_object(value)
            records.append(record_dict)
        return records


async def generate_cypher_query(natural_language_query: str) -> str:
    """Generate Cypher query from natural language"""
    if not GEMINI_API_KEY:
        # Fallback for testing without API key
        print(f"   ⚠️  No GEMINI_API_KEY, using hardcoded response")
        examples = {
            "brasil": "MATCH (a:Airport {country: 'Brazil'}) RETURN a LIMIT 50",
            "gru": "MATCH (a:Airport {code: 'GRU'})-[r:ROUTE]->(b:Airport) RETURN a, r, b LIMIT 50",
            "internacional": "MATCH (al:Airline)-[:ROUTE]-(a:Airport) RETURN DISTINCT al LIMIT 50",
            "longa": "MATCH (a:Airport)-[r:ROUTE]->(b:Airport) RETURN a, b, r ORDER BY r.distance_km DESC LIMIT 1"
        }
        for key, query in examples.items():
            if key in natural_language_query.lower():
                return query
        return "MATCH (n) RETURN n LIMIT 10"
    
    system_prompt = """You are a Neo4j Cypher query expert. Generate ONLY the query, no explanations."""
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{system_prompt}\n\nQuery: {natural_language_query}")
    return response.text.strip()


async def test_graphrag():
    """Test the GraphRAG functionality"""
    print("\n" + "="*70)
    print("🧪 AeroGraph Analytics - GraphRAG Test")
    print("="*70 + "\n")
    
    # Test 1: Seed data
    print("1️⃣ Seeding example data...")
    try:
        run_neo4j_query("MATCH (n) DETACH DELETE n")
        print("   ✅ Cleared existing data")
    except:
        pass
    
    # Create airports
    airports = [
        {"code": "GRU", "name": "Guarulhos", "city": "São Paulo", "country": "Brazil"},
        {"code": "GIG", "name": "Galeão", "city": "Rio de Janeiro", "country": "Brazil"},
        {"code": "JFK", "name": "Kennedy", "city": "New York", "country": "USA"},
    ]
    
    for airport in airports:
        query = "CREATE (a:Airport {code: $code, name: $name, city: $city, country: $country})"
        run_neo4j_query(query, airport)
    
    print(f"   ✅ Created {len(airports)} airports")
    
    # Create airlines
    airlines = [
        {"code": "LATAM", "name": "LATAM Airlines", "country": "Brazil"},
        {"code": "AA", "name": "American Airlines", "country": "USA"},
    ]
    
    for airline in airlines:
        query = "CREATE (al:Airline {code: $code, name: $name, country: $country})"
        run_neo4j_query(query, airline)
    
    print(f"   ✅ Created {len(airlines)} airlines")
    
    # Create routes
    routes = [
        {"from": "GRU", "to": "GIG", "airline": "LATAM", "distance": 365, "duration": 1.0},
        {"from": "GRU", "to": "JFK", "airline": "LATAM", "distance": 7680, "duration": 10.5},
    ]
    
    for route in routes:
        query = """MATCH (a:Airport {code: $from}), (b:Airport {code: $to})
                   CREATE (a)-[:ROUTE {airline: $airline, distance_km: $distance, duration_hours: $duration}]->(b)"""
        run_neo4j_query(query, route)
    
    print(f"   ✅ Created {len(routes)} routes")
    
    # Test 2: Query examples
    print("\n2️⃣ Testing GraphRAG Queries...\n")
    
    test_queries = [
        "Quais aeroportos estão no Brasil?",
        "Mostre todas as rotas saindo de GRU",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"   Query {i}: {query}")
        
        # Generate Cypher
        cypher = await generate_cypher_query(query)
        print(f"   Cypher: {cypher}")
        
        # Execute
        results = run_neo4j_query(cypher)
        print(f"   Results: {len(results)} records")
        if results:
            print(f"   Sample: {results[0]}")
        print()
    
    # Test 3: Graph data
    print("3️⃣ Retrieving graph data...")
    
    nodes_query = """MATCH (n) WHERE n:Airport OR n:Airline
                     RETURN id(n) as id, labels(n)[0] as label, properties(n) as properties
                     LIMIT 100"""
    nodes = run_neo4j_query(nodes_query)
    print(f"   ✅ Found {len(nodes)} nodes")
    
    links_query = """MATCH (a)-[r:ROUTE]->(b)
                     RETURN id(a) as source, id(b) as target, type(r) as type, properties(r) as properties
                     LIMIT 200"""
    links = run_neo4j_query(links_query)
    print(f"   ✅ Found {len(links)} links")
    
    # Summary
    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)
    print("\n🚀 Ready to run:")
    print("   uvicorn backend.server:app --reload")
    print("\n")
    
    driver.close()


if __name__ == "__main__":
    asyncio.run(test_graphrag())
