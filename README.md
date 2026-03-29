# SafeVoice 🛡️
**AI-Powered Legal Guidance for Women — Karnataka, India**

Built by Team Nova | PES University CSE (AIML) | Hackfinity 2025

---

## 🚀 Quick Start (5 minutes)

### Step 1 — Get a FREE Gemini API Key
1. Go to: https://aistudio.google.com/apikey
2. Sign in with your Google account (no credit card required)
3. Click "Create API Key"
4. Copy the key

### Step 2 — Add your API Key
Open `backend/.env` and paste your key:
```
GEMINI_API_KEY=paste_your_key_here
```

### Step 3 — Install & Run
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

### Step 4 — Open the App
Open your browser at: **http://localhost:8000**

That's it! 🎉

---

## 📁 Project Structure

```
safevoice/
├── backend/
│   ├── main.py              # FastAPI app — AI logic, API routes
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # API keys (NEVER commit this!)
├── frontend/
│   └── index.html           # Complete single-page app (served by backend)
├── .gitignore               # Protects .env from being committed
├── start.sh                 # Linux/Mac one-click start
├── start.bat                # Windows one-click start
└── README.md
```

---

## 🔑 Why Gemini? (Free Alternative to Anthropic)

| | Gemini 2.5 Flash (FREE) | Anthropic Claude |
|---|---|---|
| Price | **FREE** (no credit card) | $3–15 per 1M tokens |
| Daily limit | 250 requests/day | Paid only |
| Setup | Google account | Credit card required |
| Quality | Excellent | Excellent |

Gemini 2.5 Flash gives you **250 free requests per day** — more than enough for a hackathon demo!

---

## 🛡️ Security Architecture

```
User Browser  →  FastAPI Backend  →  Gemini API
                 (holds API key)
```

- API key is stored ONLY in `backend/.env`
- Frontend never sees the key
- All requests are stateless (no data stored)
- CORS configured for local development

---

## ✨ Features

- 🤖 **AI Legal Guidance** — Powered by Gemini 2.5 Flash
- 🌐 **4 Languages** — Kannada, Hindi, Telugu, English
- 👁️ **Disguise Mode** — Instant calculator overlay
- ⚡ **Quick Exit** — One click to Google
- 🔒 **Zero Data Storage** — Privacy by architecture
- 🎤 **Voice Input** — Web Speech API
- 📞 **Karnataka Helplines** — Verified, curated
- 📜 **Know Your Rights** — IPC 498A, PWDVA, POCSO

---

## 📞 Emergency Numbers

| Number | Service |
|--------|---------|
| 100 | Police Emergency |
| 181 | National Women Helpline |
| 1091 | Vanitha Sahayavani (Karnataka) |
| 1098 | Childline |
| 7827170170 | One Stop Centre |

---

## 🏆 Hackfinity 2025 — Team Nova

- Adithi B Prabhu
- Ananya J C  
- Anusha

PES University, Department of Computer Science & Engineering (AIML)
