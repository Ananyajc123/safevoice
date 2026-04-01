#!/usr/bin/env python3
"""
Test script to verify language detection and conversational responses
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_language_detection():
    """Test that bot responds in the same language as query"""
    
    test_cases = [
        {
            "name": "English - Physical Abuse",
            "message": "My husband beats me",
            "expected_lang": "en",
            "expected_keywords": ["IPC 498A", "tell me more", "How long", "evidence"]
        },
        {
            "name": "Kannada - Physical Abuse",
            "message": "ನನ್ನ ಗಂಡ ನನ್ನನ್ನು ಹೊಡೆಯುತ್ತಾನೆ",
            "expected_lang": "kn",
            "expected_keywords": ["ನಾನು ನಿಮಗೆ ಸಹಾಯ", "ಎಷ್ಟು ದಿನದಿಂದ", "ಪುರಾವೆ"]
        },
        {
            "name": "Hindi - Dowry Harassment",
            "message": "मेरे ससुराल वाले पैसे मांग रहे हैं",
            "expected_lang": "hi",
            "expected_keywords": ["दहेज", "मैं समझती हूँ", "कितने समय"]
        },
        {
            "name": "Telugu - Want to Leave",
            "message": "నేను ఇల్లు వదిలి వెళ్లాలనుకుంటున్నాను",
            "expected_lang": "te",
            "expected_keywords": ["ఆశ్రయం", "మీరు ఇప్పుడు సురక్షితంగా", "పిల్లలు"]
        },
        {
            "name": "English - Streedhan",
            "message": "My in-laws are not returning my jewellery",
            "expected_lang": "en",
            "expected_keywords": ["IPC 406", "Streedhan", "What items", "receipts"]
        }
    ]
    
    print("\n" + "="*70)
    print("🧪 Testing Language Detection & Conversational Responses")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"   Query: {test['message']}")
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": test["message"],
                "language": "en",  # Let bot auto-detect
                "history": []
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")
            
            # Check if expected keywords are in response
            found_keywords = [kw for kw in test["expected_keywords"] if kw in reply]
            
            if len(found_keywords) >= 2:  # At least 2 keywords should match
                print(f"   ✅ PASS - Language detected: {test['expected_lang']}")
                print(f"   ✅ Found keywords: {found_keywords}")
                print(f"   📄 Response preview:")
                print(f"      {reply[:200]}...")
            else:
                print(f"   ❌ FAIL - Expected keywords not found")
                print(f"   Expected: {test['expected_keywords']}")
                print(f"   Found: {found_keywords}")
                print(f"   📄 Full response:")
                print(f"      {reply[:300]}...")
        else:
            print(f"   ❌ FAIL - Status code: {response.status_code}")
        
        print()

def test_conversational_flow():
    """Test that bot asks follow-up questions"""
    
    print("\n" + "="*70)
    print("🧪 Testing Conversational Flow (Follow-up Questions)")
    print("="*70)
    
    test_message = "My husband beats me every day"
    
    print(f"\n📝 Query: {test_message}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": test_message,
            "language": "en",
            "history": []
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        reply = data.get("reply", "")
        
        # Check for follow-up questions
        follow_up_indicators = [
            "?",  # Question mark
            "tell me more",
            "How long",
            "Are you safe",
            "Do you have",
            "evidence",
            "children"
        ]
        
        found_indicators = [ind for ind in follow_up_indicators if ind.lower() in reply.lower()]
        
        if len(found_indicators) >= 3:
            print(f"   ✅ PASS - Bot is conversational")
            print(f"   ✅ Found {len(found_indicators)} follow-up indicators")
            print(f"   📄 Response:")
            print(f"      {reply}")
        else:
            print(f"   ❌ FAIL - Not enough follow-up questions")
            print(f"   Found: {found_indicators}")
            print(f"   📄 Response:")
            print(f"      {reply}")
    else:
        print(f"   ❌ FAIL - Status code: {response.status_code}")

def test_empathy():
    """Test that bot shows empathy"""
    
    print("\n" + "="*70)
    print("🧪 Testing Empathy & Emotional Support")
    print("="*70)
    
    test_message = "I'm scared and don't know what to do"
    
    print(f"\n📝 Query: {test_message}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": test_message,
            "language": "en",
            "history": []
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        reply = data.get("reply", "")
        
        # Check for empathy indicators
        empathy_words = [
            "understand",
            "brave",
            "help you",
            "here for you",
            "rights",
            "protection",
            "safe"
        ]
        
        found_empathy = [word for word in empathy_words if word.lower() in reply.lower()]
        
        if len(found_empathy) >= 3:
            print(f"   ✅ PASS - Bot shows empathy")
            print(f"   ✅ Found empathy words: {found_empathy}")
            print(f"   📄 Response:")
            print(f"      {reply[:300]}...")
        else:
            print(f"   ❌ FAIL - Not enough empathy")
            print(f"   Found: {found_empathy}")
    else:
        print(f"   ❌ FAIL - Status code: {response.status_code}")

def main():
    print("\n" + "="*70)
    print("🚀 SafeVoice Language & Conversational Tests")
    print("="*70)
    
    try:
        # Test server health
        print("\n🧪 Testing Server Health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print("   ❌ Server not responding")
            return
        
        # Run tests
        test_language_detection()
        test_conversational_flow()
        test_empathy()
        
        print("\n" + "="*70)
        print("✅ All tests completed!")
        print("="*70)
        print("\n💡 Tips:")
        print("   - Bot auto-detects language from message")
        print("   - Bot asks 3-5 follow-up questions")
        print("   - Bot shows empathy and emotional support")
        print("   - Bot provides situation-specific guidance")
        
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
