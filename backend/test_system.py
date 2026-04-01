#!/usr/bin/env python3
"""
Test script for SafeVoice Phase 2 Authentication System
Run this to verify all components are working
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("  ✅ FastAPI installed")
    except ImportError:
        print("  ❌ FastAPI not installed - run: pip install fastapi")
        return False
    
    try:
        import face_recognition
        print("  ✅ face_recognition installed")
    except ImportError:
        print("  ❌ face_recognition not installed - run: pip install face-recognition")
        return False
    
    try:
        import cv2
        print("  ✅ OpenCV installed")
    except ImportError:
        print("  ❌ OpenCV not installed - run: pip install opencv-python")
        return False
    
    try:
        import numpy
        print("  ✅ NumPy installed")
    except ImportError:
        print("  ❌ NumPy not installed - run: pip install numpy")
        return False
    
    try:
        import PIL
        print("  ✅ Pillow installed")
    except ImportError:
        print("  ❌ Pillow not installed - run: pip install Pillow")
        return False
    
    try:
        import google.generativeai
        print("  ✅ Google Generative AI installed")
    except ImportError:
        print("  ❌ Google Generative AI not installed - run: pip install google-generativeai")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\n🔍 Testing database...")
    
    try:
        from database import Database
        db = Database()
        print("  ✅ Database initialized")
        
        # Test connection
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        expected_tables = ['users', 'evidence', 'chat_history', 'fir_filings']
        found_tables = [t[0] for t in tables]
        
        for table in expected_tables:
            if table in found_tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_face_auth():
    """Test face authentication system"""
    print("\n🔍 Testing face authentication...")
    
    try:
        from face_auth import FaceAuthSystem
        face_auth = FaceAuthSystem()
        print("  ✅ Face auth system initialized")
        return True
    except Exception as e:
        print(f"  ❌ Face auth error: {e}")
        return False

def test_legal_knowledge():
    """Test legal knowledge base"""
    print("\n🔍 Testing legal knowledge base...")
    
    try:
        from legal_knowledge import LEGAL_KNOWLEDGE_BASE, get_legal_info
        
        # Test IPC 498A
        info = get_legal_info('IPC_498A')
        if info and 'title' in info:
            print("  ✅ IPC 498A information available")
        else:
            print("  ❌ IPC 498A information missing")
            return False
        
        # Test PWDVA
        info = get_legal_info('PWDVA_2005')
        if info and 'title' in info:
            print("  ✅ PWDVA 2005 information available")
        else:
            print("  ❌ PWDVA 2005 information missing")
            return False
        
        # Test helplines
        if 'EMERGENCY_HELPLINES' in LEGAL_KNOWLEDGE_BASE:
            print("  ✅ Emergency helplines available")
        else:
            print("  ❌ Emergency helplines missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Legal knowledge error: {e}")
        return False

def test_enhanced_chat():
    """Test enhanced chatbot"""
    print("\n🔍 Testing enhanced chatbot...")
    
    try:
        # Check if API key is set
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY", "")
        
        if not api_key:
            print("  ⚠️  GEMINI_API_KEY not set in .env file")
            print("     Chatbot will use fallback responses")
            return True
        
        from enhanced_chat import EnhancedChatbot
        chatbot = EnhancedChatbot(api_key)
        print("  ✅ Enhanced chatbot initialized")
        
        # Test response generation
        response = chatbot.get_response(
            user_message="What is IPC 498A?",
            language="en"
        )
        
        if response and len(response) > 0:
            print("  ✅ Chatbot generating responses")
            print(f"     Sample response: {response[:100]}...")
        else:
            print("  ❌ Chatbot not generating responses")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced chat error: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'main.py',
        'database.py',
        'face_auth.py',
        'enhanced_chat.py',
        'legal_knowledge.py',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} exists")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 60)
    print("SafeVoice Phase 2 - System Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Package Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Face Authentication", test_face_auth()))
    results.append(("Legal Knowledge Base", test_legal_knowledge()))
    results.append(("Enhanced Chatbot", test_enhanced_chat()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Start the server: uvicorn main:app --reload --port 8000")
        print("2. Open browser: http://localhost:8000/auth.html")
        print("3. Test signup with camera")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
