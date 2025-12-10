#!/usr/bin/env python3
"""
Test script to verify all connections and configurations
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

print("\n" + "="*60)
print("🔍 AeroGraph Analytics - Configuration Test")
print("="*60 + "\n")

# Test 1: Check Neo4j
print("1️⃣ Testing Neo4j Configuration...")
try:
    from neo4j import GraphDatabase
    
    neo4j_uri = os.environ.get('NEO4J_URI')
    neo4j_user = os.environ.get('NEO4J_USERNAME')
    neo4j_password = os.environ.get('NEO4J_PASSWORD')
    neo4j_database = os.environ.get('NEO4J_DATABASE')
    
    if not all([neo4j_uri, neo4j_user, neo4j_password, neo4j_database]):
        print("   ❌ Neo4j configuration incomplete")
        sys.exit(1)
    
    print(f"   URI: {neo4j_uri}")
    print(f"   User: {neo4j_user}")
    print(f"   Database: {neo4j_database}")
    
    # Try to connect
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session(database=neo4j_database) as session:
        result = session.run("RETURN 1")
        print("   ✅ Neo4j connection successful!")
    driver.close()
except Exception as e:
    print(f"   ❌ Neo4j connection failed: {str(e)}")
    sys.exit(1)

# Test 2: Check Gemini API
print("\n2️⃣ Testing Google Generative AI (Gemini)...")
try:
    import google.generativeai as genai
    
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("   ⚠️  GEMINI_API_KEY not set (optional)")
    else:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Hello' only")
        if response.text:
            print(f"   ✅ Gemini API working! Response: {response.text[:50]}")
        else:
            print("   ❌ Gemini API returned empty response")
            sys.exit(1)
except ImportError:
    print("   ❌ google-generativeai not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"   ⚠️  Gemini API error: {str(e)}")
    print("   (This is OK for demo, but required for production)")

# Test 3: Check FastAPI
print("\n3️⃣ Testing FastAPI...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI installed and working")
except ImportError:
    print("   ❌ FastAPI not installed")
    sys.exit(1)

# Test 4: Check other dependencies
print("\n4️⃣ Checking other dependencies...")
dependencies = {
    'uvicorn': 'ASGI server',
    'pydantic': 'Data validation',
    'python-dotenv': 'Environment variables',
    'neo4j': 'Database driver',
}

for pkg, description in dependencies.items():
    try:
        __import__(pkg.replace('-', '_'))
        print(f"   ✅ {pkg}: {description}")
    except ImportError:
        print(f"   ❌ {pkg}: {description} - NOT INSTALLED")
        sys.exit(1)

# Test 5: CORS Configuration
print("\n5️⃣ Checking CORS Configuration...")
cors_origins = os.environ.get('CORS_ORIGINS', '*')
print(f"   CORS_ORIGINS: {cors_origins}")
print("   ✅ Configuration loaded")

# Summary
print("\n" + "="*60)
print("✅ All configurations are valid!")
print("="*60)
print("\n🚀 You can now run:")
print("   uvicorn server:app --reload")
print("\n")
