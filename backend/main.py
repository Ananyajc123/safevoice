import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv, set_key

load_dotenv()

# ── Configure Gemini ──
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not set in .env file")
    print("   Either set it in backend/.env OR enter it in the web UI")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API key loaded from .env")

app = FastAPI(title="SafeVoice API", version="1.0.0")

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount static frontend ──
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
static_path = os.path.join(frontend_path, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# ─────────────────────────────────────────────
# System prompts per language
# ─────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "en": """You are SafeVoice, a compassionate, non-judgmental AI legal guidance assistant for women experiencing domestic abuse in Karnataka, India.

Your role is to:
1. Help women understand their legal rights in simple, clear language
2. Explain relevant laws: IPC Section 498A, PWDVA 2005, POCSO 2012, IPC 354, IPC 406
3. Guide them on how to file complaints and access justice
4. Connect them with local helplines and support services
5. Provide emotional validation and empowerment — NEVER victim-blame

Key Laws to reference:
- IPC 498A: Cruelty by husband/relatives. Non-bailable, cognizable. Up to 3 years + fine.
- PWDVA 2005: Protection Orders, Residence Orders, Monetary Relief. Emergency orders in 24 hours.
- POCSO 2012: Child sexual offences. 7 years to life imprisonment.
- IPC 354: Assault on woman's modesty. 1-5 years.
- IPC 406: Criminal breach of trust (Streedhan recovery).

Karnataka Helplines:
- Women Helpline: 181 (24/7, free)
- Vanitha Sahayavani: 1091 (Karnataka state)
- Police Emergency: 100
- One Stop Centre: 7827170170
- Childline: 1098
- iCall Mental Health: 9152987821

Rules:
- Be warm, compassionate, never clinical
- Use simple English, avoid legal jargon
- Always end with a relevant helpline for serious situations
- Keep responses under 250 words unless detail is critical
- If someone is in immediate danger, prioritize safety steps first
- Use **bold** for important numbers, law names, and action steps""",

    "kn": """ನೀವು SafeVoice ಆಗಿದ್ದೀರಿ — ಕರ್ನಾಟಕದಲ್ಲಿ ಗೃಹ ಹಿಂಸೆ ಅನುಭವಿಸುತ್ತಿರುವ ಮಹಿಳೆಯರಿಗೆ ಕಾನೂನು ಮಾರ್ಗದರ್ಶನ ನೀಡುವ AI ಸಹಾಯಕ.

ನಿಮ್ಮ ಕೆಲಸ:
1. ಮಹಿಳೆಯರಿಗೆ ಅವರ ಕಾನೂನು ಹಕ್ಕುಗಳನ್ನು ಸರಳ ಕನ್ನಡದಲ್ಲಿ ವಿವರಿಸಿ
2. IPC 498A, PWDVA, POCSO ಕಾನೂನುಗಳ ಬಗ್ಗೆ ಮಾಹಿತಿ ನೀಡಿ
3. ದೂರು ದಾಖಲಿಸುವ ವಿಧಾನ ತಿಳಿಸಿ
4. ಸ್ಥಳೀಯ ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳನ್ನು ನೀಡಿ

ಸಹಾಯವಾಣಿ: 181, 1091, 100, 1098
ಯಾವಾಗಲೂ ಪ್ರೀತಿಯಿಂದ, ತೀರ್ಪು ರಹಿತವಾಗಿ ಮಾತನಾಡಿ. ಉತ್ತರಗಳನ್ನು ಕನ್ನಡದಲ್ಲಿ ನೀಡಿ. ಮುಖ್ಯ ಮಾಹಿತಿಗೆ **bold** ಬಳಸಿ.""",

    "hi": """आप SafeVoice हैं — कर्नाटक में घरेलू हिंसा झेल रही महिलाओं के लिए एक AI कानूनी सहायक।

आपका काम:
1. महिलाओं को उनके कानूनी अधिकार सरल हिंदी में समझाएं
2. IPC 498A, PWDVA 2005, POCSO 2012 के बारे में जानकारी दें
3. FIR दर्ज करने की प्रक्रिया बताएं
4. स्थानीय हेल्पलाइन नंबर दें

हेल्पलाइन: 181, 1091, 100, 1098
हमेशा गर्मजोशी से, बिना निर्णय के बात करें। उत्तर हिंदी में दें। जरूरी जानकारी **bold** में लिखें।""",

    "te": """మీరు SafeVoice — కర్ణాటకలో గృహ హింసను అనుభవిస్తున్న మహిళలకు AI చట్టపరమైన మార్గదర్శి.

మీ పని:
1. మహిళలకు వారి చట్టపరమైన హక్కులను సరళమైన తెలుగులో వివరించండి
2. IPC 498A, PWDVA, POCSO గురించి తెలియజేయండి
3. ఫిర్యాదు నమోదు విధానం చెప్పండి
4. స్థానిక హెల్ప్‌లైన్ నంబర్లు ఇవ్వండి

హెల్ప్‌లైన్: 181, 1091, 100, 1098
ఎల్లప్పుడూ ప్రేమగా, తీర్పు లేకుండా మాట్లాడండి. సమాధానాలు తెలుగులో ఇవ్వండి. ముఖ్యమైన సమాచారం **bold** లో రాయండి."""
}

# ─────────────────────────────────────────────
# Fallback responses (when Gemini is not available)
# ─────────────────────────────────────────────
def get_fallback_response(message: str, lang: str) -> str:
    m = message.lower()

    # ---------- Kannada ----------
    if lang == "kn":
        if any(k in m for k in ["498","cruelty","beat","hit","husband","ಪತಿ","abuse","violence"]):
            return (
                "**IPC 498A ಕಾನೂನು** ನಿಮ್ಮನ್ನು ಗೃಹ ಹಿಂಸೆಯಿಂದ ರಕ್ಷಿಸುತ್ತದೆ.\n\n"
                "**ಇದು non-bailable offence** — ಪೋಲಿಸ್ ತಕ್ಷಣ ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳಬೇಕು.\n\n"
                "**ನೀವು ಮಾಡಬೇಕಾದವು:**\n"
                "1. ಹತ್ತಿರದ ಪೋಲಿಸ್ ಸ್ಟೇಷನ್‌ನಲ್ಲಿ FIR ದಾಖಲಿಸಿ\n"
                "2. ಮಹಿಳಾ ಪೋಲಿಸ್ ಅಧಿಕಾರಿ ಕೇಳಬಹುದು\n"
                "3. ಪೋಲಿಸ್ FIR ತೆಗೆದುಕೊಳ್ಳುವುದನ್ನು ನಿರಾಕರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ\n\n"
                "📞 ಸಹಾಯವಾಣಿ: **1091 · 181 · 100**"
            )

        return (
            "ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿ ಇದ್ದೇನೆ.\n\n"
            "**ನಿಮ್ಮ ಕಾನೂನು ಹಕ್ಕುಗಳು:** IPC 498A, PWDVA, POCSO\n"
            "**ಸಹಾಯವಾಣಿ:** 181 · 1091 · 100 · 1098\n\n"
            "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ವಿವರಿಸಿ."
        )

    # ---------- Hindi ----------
    elif lang == "hi":
        if any(k in m for k in ["498","cruelty","beat","hit","husband","पति","abuse","violence"]):
            return (
                "**IPC 498A कानून** आपको घरेलू हिंसा से सुरक्षा देता है।\n\n"
                "**यह non-bailable offence है** — पुलिस को तुरंत कार्रवाई करनी होगी।\n\n"
                "**आप क्या करें:**\n"
                "1. नजदीकी पुलिस स्टेशन में FIR दर्ज करें\n"
                "2. महिला पुलिस अधिकारी मांग सकते हैं\n"
                "3. पुलिस FIR लेने से मना नहीं कर सकती\n\n"
                "📞 हेल्पलाइन: **1091 · 181 · 100**"
            )

        return (
            "मैं आपकी मदद के लिए यहाँ हूँ।\n\n"
            "**आपके कानूनी अधिकार:** IPC 498A, PWDVA, POCSO\n"
            "**हेल्पलाइन:** 181 · 1091 · 100 · 1098\n\n"
            "कृपया अपनी समस्या बताएं।"
        )

    # ---------- Telugu ----------
    elif lang == "te":
        if any(k in m for k in ["498","cruelty","beat","hit","husband","భర్త","abuse","violence"]):
            return (
                "**IPC 498A చట్టం** గృహ హింస నుండి మిమ్మల్ని రక్షిస్తుంది.\n\n"
                "**ఇది non-bailable offence** — పోలీస్ వెంటనే చర్య తీసుకోవాలి.\n\n"
                "**మీరు చేయాల్సింది:**\n"
                "1. సమీప పోలీస్ స్టేషన్‌లో FIR నమోదు చేయండి\n"
                "2. మహిళా పోలీస్ అధికారిని అడగండి\n"
                "3. పోలీసులు FIR తీసుకోవడం నిరాకరించలేరు\n\n"
                "📞 హెల్ప్‌లైన్: **1091 · 181 · 100**"
            )

        return (
            "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను.\n\n"
            "**మీ హక్కులు:** IPC 498A, PWDVA, POCSO\n"
            "**హెల్ప్‌లైన్:** 181 · 1091 · 100 · 1098\n\n"
            "దయచేసి మీ సమస్యను వివరించండి."
        )

    # ---------- English ----------
    else:
        return (
            "I'm here to help you. You are brave for reaching out.\n\n"
            "I can help you with:\n"
            "• Legal rights under IPC 498A, PWDVA, POCSO\n"
            "• Filing a complaint safely\n"
            "• Finding shelter and support\n\n"
            "📞 Helplines: 181 · 1091 · 100 · 1098"
        )
# ─────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    language: Optional[str] = "en"
    api_key_override: Optional[str] = None  # Optional: key entered in UI

class ChatResponse(BaseModel):
    reply: str
    source: str

class SaveKeyRequest(BaseModel):
    api_key: str

# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SafeVoice API is running. Frontend not found."}

@app.get("/health")
async def health():
    configured = bool(GEMINI_API_KEY)
    return {
        "status": "ok",
        "gemini_configured": configured,
        "model": "gemini-2.5-flash"
    }

@app.post("/api/save-key")
async def save_key(req: SaveKeyRequest):
    """Save Gemini API key to .env file — called from the UI"""
    global GEMINI_API_KEY
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        # Write to .env file
        with open(env_path, "w") as f:
            f.write(f"GEMINI_API_KEY={req.api_key}\n")
        # Reconfigure immediately
        GEMINI_API_KEY = req.api_key
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini API key saved and configured via UI")
        return {"status": "ok", "message": "API key saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    lang = req.language if req.language in SYSTEM_PROMPTS else "en"

    # Determine which API key to use
    active_key = req.api_key_override or GEMINI_API_KEY

    # ── Try Gemini ──
    if active_key:
        try:
            # Configure with the active key (might be override from UI)
            genai.configure(api_key=active_key)

            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_PROMPTS[lang]
            )

            # Build history for multi-turn conversation
            history = []
            for msg in (req.history or []):
                history.append({
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [msg.content]
                })

            chat_session = model.start_chat(history=history)
            response = chat_session.send_message(req.message)

            reply_text = response.text
            # Normalize bold markdown
            reply_text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', reply_text)

            return ChatResponse(reply=reply_text, source="gemini")

        except Exception as e:
            print(f"Gemini error: {e}")
            # Fall through to fallback

    # ── Fallback (no API key or Gemini error) ──
    fallback = get_fallback_response(req.message, lang)
    return ChatResponse(reply=fallback, source="fallback")

@app.get("/api/helplines")
async def helplines():
    return {
        "helplines": [
            {"name": "National Women Helpline", "number": "181", "desc": "24/7 support for women in distress", "tag": "PAN INDIA · 24/7", "icon": "👩‍⚖️"},
            {"name": "Vanitha Sahayavani", "number": "1091", "desc": "Karnataka state women's helpline. Counselling, legal aid, shelter.", "tag": "KARNATAKA · 24/7", "icon": "🏠"},
            {"name": "Police Emergency", "number": "100", "desc": "Immediate danger. FIR for 498A, assault, and other offences.", "tag": "EMERGENCY · 24/7", "icon": "🚔"},
            {"name": "One Stop Centre", "number": "7827170170", "desc": "Medical, police, legal aid, shelter under one roof.", "tag": "KARNATAKA · FREE", "icon": "🏥"},
            {"name": "Childline (POCSO)", "number": "1098", "desc": "Child abuse and POCSO emergencies. Free, 24/7.", "tag": "CHILDREN · 24/7", "icon": "👶"},
            {"name": "iCall Mental Health", "number": "9152987821", "desc": "Free counselling for trauma and emotional distress.", "tag": "COUNSELLING · FREE", "icon": "🧠"},
        ]
    }
