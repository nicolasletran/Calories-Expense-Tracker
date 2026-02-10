# backend/test_api.py
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_all_endpoints():
    tests = []
    
    # Test 1: Get all entries
    try:
        response = requests.get(f"{BASE_URL}/entries")
        tests.append(("GET /entries", response.status_code == 200))
    except:
        tests.append(("GET /entries", False))
    
    # Test 2: Add new entry
    try:
        new_meal = {
            "food": "Test Meal",
            "calories": 300,
            "protein": 25,
            "category": "Snack",
            "date": "2024-01-01"
        }
        response = requests.post(f"{BASE_URL}/entries", 
                               json=new_meal)
        tests.append(("POST /entries", response.status_code == 201))
    except:
        tests.append(("POST /entries", False))
    
    # Test 3: Get today's summary
    try:
        response = requests.get(f"{BASE_URL}/summary/today")
        tests.append(("GET /summary/today", response.status_code == 200))
    except:
        tests.append(("GET /summary/today", False))
    
    # Print results
    print("\n" + "="*40)
    print("API Test Results")
    print("="*40)
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    return all(passed for _, passed in tests)

if __name__ == "__main__":
    success = test_all_endpoints()
    exit(0 if success else 1)