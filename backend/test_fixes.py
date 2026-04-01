#!/usr/bin/env python3
"""
Quick test script to verify all fixes are working
Run this after starting the server with: uvicorn main_demo:app --reload --port 8000
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat_endpoint():
    """Test the chat endpoint with legal queries"""
    print("\n🧪 Testing Chat Endpoint...")
    
    test_cases = [
        {
            "message": "My husband beats me",
            "expected_keywords": ["498A", "cruelty", "police"]
        },
        {
            "message": "I need protection from domestic violence",
            "expected_keywords": ["PWDVA", "Protection", "Order"]
        },
        {
            "message": "How do I file FIR",
            "expected_keywords": ["FIR", "police", "station"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n  Test {i}: '{test['message']}'")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": test["message"],
                "language": "en",
                "history": []
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            
            # Check if expected keywords are in response
            found_keywords = [kw for kw in test["expected_keywords"] if kw.lower() in reply.lower()]
            
            if found_keywords:
                print(f"  ✅ PASS - Found keywords: {found_keywords}")
                print(f"  📝 Response preview: {reply[:150]}...")
            else:
                print(f"  ❌ FAIL - Expected keywords not found: {test['expected_keywords']}")
                print(f"  📝 Response: {reply[:200]}...")
        else:
            print(f"  ❌ FAIL - Status code: {response.status_code}")

def test_fir_filing():
    """Test FIR filing endpoint"""
    print("\n🧪 Testing FIR Filing Endpoint...")
    
    fir_data = {
        "user_id": "test_user_123",
        "complainant_name": "Test User",
        "complainant_phone": "9876543210",
        "complainant_address": "Test Address, Bangalore",
        "accused_details": "Husband - John Doe",
        "incident_details": "Test incident for verification",
        "laws_invoked": "IPC 498A, PWDVA 2005"
    }
    
    print(f"\n  Filing test FIR...")
    response = requests.post(
        f"{BASE_URL}/api/fir/file",
        json=fir_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            case_id = data.get("case_id")
            print(f"  ✅ PASS - FIR filed successfully")
            print(f"  📋 Case ID: {case_id}")
            return case_id
        else:
            print(f"  ❌ FAIL - {data.get('message')}")
    else:
        print(f"  ❌ FAIL - Status code: {response.status_code}")
    
    return None

def test_get_firs(user_id):
    """Test retrieving FIRs"""
    print(f"\n🧪 Testing Get FIRs Endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/fir/{user_id}")
    
    if response.status_code == 200:
        data = response.json()
        firs = data.get("firs", [])
        print(f"  ✅ PASS - Retrieved {len(firs)} FIR(s)")
        if firs:
            print(f"  📋 Latest FIR: {firs[0].get('case_details', '')[:100]}...")
    else:
        print(f"  ❌ FAIL - Status code: {response.status_code}")

def test_helplines():
    """Test helplines endpoint"""
    print("\n🧪 Testing Helplines Endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/helplines")
    
    if response.status_code == 200:
        data = response.json()
        helplines = data.get("helplines", [])
        print(f"  ✅ PASS - Retrieved {len(helplines)} helpline(s)")
        for hl in helplines[:3]:
            print(f"  📞 {hl.get('number')}: {hl.get('name')}")
    else:
        print(f"  ❌ FAIL - Status code: {response.status_code}")

def main():
    print("=" * 60)
    print("🚀 SafeVoice Backend Tests")
    print("=" * 60)
    
    try:
        # Test health check
        print("\n🧪 Testing Server Health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("  ✅ Server is running")
        else:
            print("  ❌ Server not responding")
            return
        
        # Run tests
        test_chat_endpoint()
        case_id = test_fir_filing()
        if case_id:
            test_get_firs("test_user_123")
        test_helplines()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn main_demo:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
