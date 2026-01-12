"""API testing script for Travel Agent."""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(name: str, method: str, endpoint: str, data: Dict = None) -> bool:
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        
        print(f"✓ {name}: PASSED")
        return True
        
    except Exception as e:
        print(f"✗ {name}: FAILED - {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Travel Agent API\n")
    
    tests = [
        ("Health Check", "GET", "/health"),
        ("Root Endpoint", "GET", "/"),
        ("List Modes", "GET", "/modes"),
        ("List Tools", "GET", "/tools"),
        ("Query - Suggest Places", "POST", "/query", 
         {"query": "suggest places in Chiang Mai"}),
        ("Query - Itinerary", "POST", "/query", 
         {"query": "plan 3 day hiking trip"}),
        ("Query - Describe Place", "POST", "/query", 
         {"query": "tell me about Doi Inthanon"}),
        ("Query - Mode Override", "POST", "/query", 
         {"query": "test", "mode": "suggest_places"}),
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test_endpoint(*test):
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
        exit(1)

if __name__ == "__main__":
    main()