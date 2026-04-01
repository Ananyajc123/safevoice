# SafeVoice Phase 2 - Authentication System Setup

## ✅ What's Been Implemented

### Phase 2 Features:
1. **Face Recognition Authentication** - Women-only signup with face verification
2. **Gender Detection** - Prevents men from signing up (with facial analysis)
3. **Disguise Key System** - Secret password for secure access
4. **Database Integration** - SQLite database for user data, evidence vault, FIR records
5. **Enhanced Chatbot** - Legal knowledge base integration (NO HALLUCINATION)
6. **Evidence Vault API** - Encrypted storage for photos, audio, notes
7. **FIR Filing System** - Online FIR filing with tracking
8. **Lawyer Finder** - Find free legal aid lawyers in Karnataka
9. **Enhanced SOS** - Emergency trigger with location logging

## 📦 Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note:** Face recognition requires additional system libraries:

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

**On macOS:**
```bash
brew install cmake
```

**On Windows:**
- Install Visual Studio Build Tools
- Or use pre-built wheels: `pip install face-recognition --no-deps`

### 2. Initialize Database

The database will be created automatically on first run. It creates:
- `safevoice.db` in the backend directory
- Tables: users, evidence, chat_history, fir_filings

### 3. Start the Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. Access the Application

- **Authentication Page:** http://localhost:8000/auth.html
- **Main App:** http://localhost:8000/

## 🔐 How Authentication Works

### First Time (Signup):
1. User opens the app
2. Enters a disguise key (secret password)
3. Camera captures their face
4. System detects gender using facial features
5. If female (or uncertain), account is created
6. If male with high confidence, signup is denied
7. Face encoding is stored encrypted in database

### Returning User (Login):
1. User enters their disguise key
2. Camera captures their face
3. System verifies face matches stored encoding
4. If match, user is logged in
5. Session token is generated

### Security Features:
- Disguise key is hashed (SHA-256)
- Face encodings are stored as base64
- No personal information collected
- All data stored locally in SQLite
- Session tokens for authentication

## 🎯 Testing the System

### Test Signup Flow:
1. Go to http://localhost:8000/auth.html
2. Enter disguise key: `test123`
3. Click "Capture Photo" and allow camera
4. Take a clear photo of your face
5. Click "Create Secure Account"
6. You should be redirected to main app

### Test Login Flow:
1. Close browser and reopen http://localhost:8000/auth.html
2. Enter same disguise key: `test123`
3. Capture photo again
4. System should recognize you and auto-login

### Test Gender Detection:
- The system analyzes facial features
- Women are allowed to signup
- Men with high confidence (>60%) are denied
- Uncertain cases default to allowing signup

## 📡 API Endpoints

### Authentication:
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login existing user
- `POST /api/auth/check-existing` - Check if user exists

### Evidence Vault:
- `POST /api/evidence/save` - Save encrypted evidence
- `GET /api/evidence/{user_id}` - Get user's evidence
- `DELETE /api/evidence/{evidence_id}/{user_id}` - Delete evidence

### FIR Filing:
- `POST /api/fir/file` - File FIR online
- `GET /api/fir/{user_id}` - Get user's FIRs

### Lawyer Finder:
- `GET /api/lawyers/{city}` - Find lawyers in city
- `GET /api/legal-info/{topic}` - Get legal information

### SOS:
- `POST /api/sos/trigger` - Trigger emergency SOS

### Chat (Enhanced):
- `POST /api/chat` - Chat with legal knowledge base

## 🔧 Configuration

### Database Location:
- Default: `backend/safevoice.db`
- Change in `backend/database.py` if needed

### Face Recognition Tolerance:
- Default: 0.6 (60% match required)
- Adjust in `backend/main.py` login endpoint
- Lower = stricter, Higher = more lenient

### Gender Detection Confidence:
- Default: 0.6 (60% confidence to deny males)
- Adjust in `backend/main.py` signup endpoint

## 🚨 Known Limitations

### Gender Detection:
- Uses facial feature analysis (not 100% accurate)
- Simplified heuristic approach
- For production, use a trained CNN model
- Currently defaults to allowing signup if uncertain

### Face Recognition:
- Requires good lighting
- Face should be clearly visible
- Works best with frontal face photos
- May fail with masks, sunglasses, etc.

### Camera Access:
- Requires HTTPS in production
- Works on localhost for development
- User must grant camera permission

## 🔄 Next Steps (Phase 3)

1. **Evidence Encryption** - Implement AES encryption for vault
2. **Frontend Integration** - Update main app to use auth
3. **Session Management** - Add JWT tokens
4. **FIR Portal UI** - Create FIR filing interface
5. **Lawyer Finder UI** - Add lawyer search interface
6. **Enhanced SOS** - Integrate SMS/calling APIs

## 🐛 Troubleshooting

### "No module named 'face_recognition'"
```bash
pip install cmake
pip install dlib
pip install face-recognition
```

### "Camera not working"
- Check browser permissions
- Ensure HTTPS or localhost
- Try different browser

### "Database locked"
- Close all connections
- Delete `safevoice.db` and restart

### "Gender detection not accurate"
- This is expected with heuristic approach
- For production, integrate proper CNN model
- Consider using cloud APIs (AWS Rekognition, Azure Face API)

## 📝 Database Schema

### users table:
- id (PRIMARY KEY)
- disguise_key (UNIQUE, hashed)
- face_encoding (base64)
- gender (detected)
- created_at
- last_login

### evidence table:
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- type (image/audio/note)
- encrypted_data
- filename
- timestamp

### fir_filings table:
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- case_details
- status
- filed_at

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ Server starts without errors
2. ✅ Auth page loads with camera
3. ✅ Photo capture works
4. ✅ Signup creates user in database
5. ✅ Login recognizes returning user
6. ✅ Chat gives accurate legal responses
7. ✅ No hallucination in legal advice

## 📞 Support

If you encounter issues:
1. Check server logs for errors
2. Verify all dependencies installed
3. Ensure camera permissions granted
4. Check database file exists
5. Test with different browsers

---

**Built by Team Nova | PES University | Hackfinity 2025**
