# 🚀 SafeVoice Phase 2 - Quick Start

## ⚡ 3-Minute Setup

### Step 1: Install (1 minute)
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Test (30 seconds)
```bash
python test_system.py
```

### Step 3: Run (30 seconds)
```bash
uvicorn main:app --reload --port 8000
```

### Step 4: Open Browser
**http://localhost:8000/auth.html**

---

## 🎯 First Test

1. Enter disguise key: `test123`
2. Click "Capture Photo"
3. Allow camera
4. Take photo
5. Click "Create Secure Account"
6. ✅ Should redirect to main app

---

## 📊 What's Working

✅ Face recognition authentication  
✅ Gender detection (women-only)  
✅ Legal knowledge base (no hallucination)  
✅ Enhanced chatbot  
✅ Evidence vault API  
✅ FIR filing system  
✅ Lawyer finder  
✅ SOS emergency  

---

## 🔗 Important URLs

- **Auth Page:** http://localhost:8000/auth.html
- **Main App:** http://localhost:8000/
- **API Docs:** http://localhost:8000/docs
- **Test Endpoint:** http://localhost:8000/health

---

## 🧪 Quick API Tests

### Test Chatbot:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is IPC 498A?","language":"en"}'
```

### Test Lawyer Finder:
```bash
curl http://localhost:8000/api/lawyers/bangalore
```

### Test Legal Info:
```bash
curl http://localhost:8000/api/legal-info/IPC_498A
```

---

## 📚 Documentation

- **README_PHASE2.md** - Start here
- **SETUP_PHASE2.md** - Detailed setup
- **PHASE2_COMPLETE.md** - All features
- **ARCHITECTURE.md** - System design
- **IMPLEMENTATION_SUMMARY.md** - What's built

---

## 🐛 Quick Fixes

### Camera not working?
- Allow camera in browser
- Use Chrome or Firefox
- Check HTTPS/localhost

### face_recognition error?
```bash
# Ubuntu/Debian
sudo apt-get install cmake libopenblas-dev
pip install face-recognition

# macOS
brew install cmake
pip install face-recognition
```

### Database locked?
```bash
rm backend/safevoice.db
python backend/test_system.py
```

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Test script passes
- [ ] Server starts
- [ ] Auth page loads
- [ ] Camera works
- [ ] Signup creates user
- [ ] Login works
- [ ] Chatbot responds

---

## 🎉 You're Ready!

**Phase 2 is complete. All features working.**

**Next:** Phase 3 - Frontend Integration

---

**Team Nova | PES University | Hackfinity 2025**
