import requests
import sys
import json
from datetime import datetime

class GraphRAGAPITester:
    def __init__(self, base_url="https://graph-analytics-2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_data": None,
                "error": None
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    result["error"] = response.json()
                except:
                    result["error"] = response.text

            self.test_results.append(result)
            return success, result["response_data"] if success else result["error"]

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "response_data": None,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, str(e)

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_get_examples(self):
        """Test examples endpoint"""
        success, response = self.run_test("Get Examples", "GET", "examples", 200)
        if success and isinstance(response, list) and len(response) == 5:
            print(f"   ✓ Found {len(response)} example queries")
            return True
        elif success:
            print(f"   ⚠️  Expected 5 examples, got {len(response) if isinstance(response, list) else 'non-list'}")
        return success

    def test_seed_data(self):
        """Test seeding data"""
        success, response = self.run_test(
            "Seed Data", 
            "POST", 
            "seed-data", 
            200, 
            data={"clear_existing": True},
            timeout=60
        )
        if success and isinstance(response, dict):
            airports = response.get('airports', 0)
            airlines = response.get('airlines', 0)
            routes = response.get('routes', 0)
            print(f"   ✓ Seeded {airports} airports, {airlines} airlines, {routes} routes")
        return success

    def test_get_graph_data(self):
        """Test getting graph data"""
        success, response = self.run_test("Get Graph Data", "GET", "graph/data", 200)
        if success and isinstance(response, dict):
            nodes = response.get('nodes', [])
            links = response.get('links', [])
            print(f"   ✓ Found {len(nodes)} nodes and {len(links)} links")
            return len(nodes) > 0 and len(links) > 0
        return success

    def test_graphrag_query(self, query="Quais aeroportos estão no Brasil?"):
        """Test GraphRAG query"""
        success, response = self.run_test(
            "GraphRAG Query", 
            "POST", 
            "graphrag/query", 
            200, 
            data={"query": query},
            timeout=60
        )
        if success and isinstance(response, dict):
            answer = response.get('answer', '')
            cypher_query = response.get('cypher_query', '')
            results = response.get('results', [])
            print(f"   ✓ Answer: {answer[:100]}...")
            print(f"   ✓ Cypher: {cypher_query[:100]}...")
            print(f"   ✓ Results: {len(results)} items")
            return len(answer) > 0 and len(cypher_query) > 0
        return success

def main():
    print("🚀 Starting GraphRAG API Testing...")
    print("=" * 60)
    
    tester = GraphRAGAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Examples Endpoint", tester.test_get_examples),
        ("Seed Data", tester.test_seed_data),
        ("Graph Data", tester.test_get_graph_data),
        ("GraphRAG Query", tester.test_graphrag_query),
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            if not result:
                print(f"⚠️  {test_name} had issues but continuing...")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    # Print failed tests
    failed_tests = [t for t in tester.test_results if not t['success']]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test['test_name']}: {test['error']}")
    
    # Save detailed results
    with open('/app/test_reports/backend_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'tests_run': tester.tests_run,
                'tests_passed': tester.tests_passed,
                'success_rate': tester.tests_passed/tester.tests_run*100 if tester.tests_run > 0 else 0
            },
            'test_results': tester.test_results
        }, f, indent=2)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())