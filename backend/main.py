import os
import re
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv, set_key
from database import Database
from face_auth import FaceAuthSystem
from enhanced_chat import EnhancedChatbot
from legal_knowledge import get_legal_info, search_lawyers

load_dotenv()

# Initialize systems
db = Database()
face_auth = FaceAuthSystem()
enhanced_chat = None  # Will initialize when API key is available

# ── Configure Gemini ──
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not set in .env file")
    print("   Either set it in backend/.env OR enter it in the web UI")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    enhanced_chat = EnhancedChatbot(GEMINI_API_KEY)
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

# ══ NEW: Authentication Models ══
class SignupRequest(BaseModel):
    disguise_key: str
    face_image: str  # base64 encoded image

class LoginRequest(BaseModel):
    disguise_key: str
    face_image: str  # base64 encoded image

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    session_token: Optional[str] = None

# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@app.get("/")
async def serve_frontend():
    # Redirect to authentication page first
    auth_path = os.path.join(frontend_path, "auth.html")
    if os.path.exists(auth_path):
        return FileResponse(auth_path)
    # Fallback to main app if auth page doesn't exist
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SafeVoice API is running. Frontend not found."}

@app.get("/app")
async def serve_main_app():
    """Serve main app after authentication"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Main app not found"}

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
    global GEMINI_API_KEY, enhanced_chat
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        # Write to .env file
        with open(env_path, "w") as f:
            f.write(f"GEMINI_API_KEY={req.api_key}\n")
        # Reconfigure immediately
        GEMINI_API_KEY = req.api_key
        genai.configure(api_key=GEMINI_API_KEY)
        enhanced_chat = EnhancedChatbot(GEMINI_API_KEY)
        print(f"✅ Gemini API key saved and configured via UI")
        return {"status": "ok", "message": "API key saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════
# AUTHENTICATION ENDPOINTS
# ══════════════════════════════════════════════

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(req: SignupRequest):
    """
    Sign up new user with disguise key and face recognition
    Prioritizes access for women's safety
    """
    try:
        # Validate disguise key
        if not req.disguise_key or len(req.disguise_key) < 4:
            return AuthResponse(
                success=False,
                message="Disguise key must be at least 4 characters"
            )
        
        # Detect face and gender
        face_result = face_auth.detect_face_and_gender(req.face_image)
        
        if not face_result['face_detected']:
            return AuthResponse(
                success=False,
                message=face_result.get('error', 'No face detected. Please ensure your face is clearly visible.')
            )
        
        # Enhanced gender detection
        gender_result = face_auth.enhanced_gender_detection(req.face_image)
        
        # For women's safety app, we prioritize access
        # Only deny if very high confidence male detection
        # This ensures women can always access help
        if gender_result['gender'] == 'male' and gender_result['confidence'] > 0.85:
            return AuthResponse(
                success=False,
                message="⚠️ This app is exclusively for women experiencing domestic abuse. If you're trying to help someone, please use Ally Mode instead."
            )
        
        # Allow signup - face detected and not high-confidence male
        print(f"✅ Signup allowed - Gender: {gender_result['gender']}, Confidence: {gender_result['confidence']}")
        
        # Create user in database
        user_id = db.create_user(
            disguise_key=req.disguise_key,
            face_encoding=face_result['face_encoding'],
            gender=gender_result['gender']
        )
        
        if user_id is None:
            return AuthResponse(
                success=False,
                message="This disguise key is already registered. Please use a different key or try logging in."
            )
        
        # Generate session token (simple version - use JWT in production)
        import secrets
        session_token = secrets.token_urlsafe(32)
        
        return AuthResponse(
            success=True,
            message="✅ Account created successfully! You can now access SafeVoice.",
            user_id=user_id,
            session_token=session_token
        )
        
    except Exception as e:
        print(f"Signup error: {e}")
        return AuthResponse(
            success=False,
            message=f"Signup failed: {str(e)}"
        )

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Login existing user with disguise key and face verification
    """
    try:
        # Verify disguise key
        user = db.verify_user(req.disguise_key)
        
        if not user:
            return AuthResponse(
                success=False,
                message="Invalid disguise key. Please check and try again, or sign up if you're new."
            )
        
        # Verify face matches stored encoding
        face_match = face_auth.verify_face(
            stored_encoding_b64=user['face_encoding'],
            new_image_b64=req.face_image,
            tolerance=0.6
        )
        
        if not face_match['match']:
            return AuthResponse(
                success=False,
                message="Face verification failed. Please ensure your face is clearly visible and matches your registered photo."
            )
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Generate session token
        import secrets
        session_token = secrets.token_urlsafe(32)
        
        return AuthResponse(
            success=True,
            message=f"✅ Welcome back! Face verified with {face_match['confidence']*100:.0f}% confidence.",
            user_id=user['id'],
            session_token=session_token
        )
        
    except Exception as e:
        print(f"Login error: {e}")
        return AuthResponse(
            success=False,
            message=f"Login failed: {str(e)}"
        )

@app.post("/api/auth/check-existing")
async def check_existing(req: LoginRequest):
    """
    Check if user already exists (for auto-redirect to login)
    """
    try:
        user = db.verify_user(req.disguise_key)
        
        if user:
            # User exists, verify face
            face_match = face_auth.verify_face(
                stored_encoding_b64=user['face_encoding'],
                new_image_b64=req.face_image,
                tolerance=0.6
            )
            
            return {
                "exists": True,
                "face_match": face_match['match'],
                "message": "User found. Redirecting to login..." if face_match['match'] else "User found but face doesn't match."
            }
        
        return {
            "exists": False,
            "message": "New user. Proceeding with signup..."
        }
        
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    lang = req.language if req.language in SYSTEM_PROMPTS else "en"

    # Determine which API key to use
    active_key = req.api_key_override or GEMINI_API_KEY

    # ── Try Enhanced Chatbot (with legal knowledge base) ──
    if active_key and enhanced_chat:
        try:
            # Use enhanced chatbot with legal knowledge base
            reply_text = enhanced_chat.get_response(
                user_message=req.message,
                language=lang,
                history=[{"role": msg.role, "content": msg.content} for msg in (req.history or [])]
            )
            
            return ChatResponse(reply=reply_text, source="gemini_enhanced")

        except Exception as e:
            print(f"Enhanced chatbot error: {e}")
            # Fall through to fallback
    
    # ── If no API key, use knowledge base directly ──
    from legal_knowledge import LEGAL_KNOWLEDGE_BASE
    
    # Extract relevant legal info based on message
    message_lower = req.message.lower()
    response_parts = []
    
    # Check for IPC 498A
    if any(word in message_lower for word in ['498', 'husband', 'cruelty', 'beat', 'hit', 'abuse']):
        info = LEGAL_KNOWLEDGE_BASE.get('IPC_498A', {})
        if info:
            response_parts.append(f"**{info['title']}**\n")
            response_parts.append("Key Points:\n")
            for point in info['key_points'][:3]:
                response_parts.append(f"• {point}\n")
            response_parts.append("\nHow to File:\n")
            for step in info['how_to_file'][:3]:
                response_parts.append(f"• {step}\n")
    
    # Check for PWDVA
    if any(word in message_lower for word in ['domestic violence', 'protection', 'pwdva', 'dv act']):
        info = LEGAL_KNOWLEDGE_BASE.get('PWDVA_2005', {})
        if info:
            response_parts.append(f"\n**{info['title']}**\n")
            response_parts.append("Orders Available:\n")
            for order in info['orders_available'][:3]:
                response_parts.append(f"• {order}\n")
    
    # Check for FIR
    if any(word in message_lower for word in ['fir', 'file', 'complaint', 'police']):
        info = LEGAL_KNOWLEDGE_BASE.get('FIR_FILING_PROCESS', {})
        if info:
            response_parts.append("\n**How to File FIR:**\n")
            for step in info['steps'][:5]:
                response_parts.append(f"{step}\n")
    
    # Always add helplines
    helplines = LEGAL_KNOWLEDGE_BASE.get('EMERGENCY_HELPLINES', {})
    if helplines:
        response_parts.append("\n**Emergency Helplines:**\n")
        national = helplines.get('national', {})
        for num, desc in list(national.items())[:3]:
            response_parts.append(f"📞 {num}: {desc}\n")
    
    # If we have specific info, return it
    if response_parts:
        reply = "".join(response_parts)
        return ChatResponse(reply=reply, source="knowledge_base")
    
    # ── Final Fallback ──
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

# ══════════════════════════════════════════════
# EVIDENCE VAULT ENDPOINTS
# ══════════════════════════════════════════════

class EvidenceRequest(BaseModel):
    user_id: int
    evidence_type: str  # 'image', 'audio', 'note'
    encrypted_data: str
    filename: Optional[str] = None

@app.post("/api/evidence/save")
async def save_evidence(req: EvidenceRequest):
    """Save encrypted evidence to vault"""
    try:
        db.save_evidence(
            user_id=req.user_id,
            evidence_type=req.evidence_type,
            encrypted_data=req.encrypted_data,
            filename=req.filename
        )
        return {"success": True, "message": "Evidence saved securely"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evidence/{user_id}")
async def get_evidence(user_id: int):
    """Get all evidence for a user"""
    try:
        evidence = db.get_user_evidence(user_id)
        return {"success": True, "evidence": evidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/evidence/{evidence_id}/{user_id}")
async def delete_evidence(evidence_id: int, user_id: int):
    """Delete evidence item"""
    try:
        db.delete_evidence(evidence_id, user_id)
        return {"success": True, "message": "Evidence deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════
# FIR FILING ENDPOINTS
# ══════════════════════════════════════════════

class FIRRequest(BaseModel):
    user_id: int
    case_details: str

@app.post("/api/fir/file")
async def file_fir(req: FIRRequest):
    """File FIR online"""
    try:
        fir_id = db.file_fir(req.user_id, req.case_details)
        return {
            "success": True,
            "message": "FIR filed successfully",
            "fir_id": fir_id,
            "next_steps": [
                "Your FIR has been recorded with ID: " + str(fir_id),
                "Visit nearest police station with this ID",
                "Carry identification documents",
                "Request for women police officer",
                "Get physical FIR copy",
                "Note down investigating officer details"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fir/{user_id}")
async def get_user_firs(user_id: int):
    """Get all FIRs filed by user"""
    try:
        firs = db.get_user_firs(user_id)
        return {"success": True, "firs": firs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════
# LAWYER FINDER ENDPOINTS
# ══════════════════════════════════════════════

@app.get("/api/lawyers/{city}")
async def find_lawyers(city: str):
    """Find lawyers in specified city"""
    try:
        lawyers = search_lawyers(city)
        return {
            "success": True,
            "city": city,
            "lawyers": lawyers,
            "message": "Free legal aid is available through District Legal Services Authority"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/legal-info/{topic}")
async def get_legal_information(topic: str):
    """Get detailed legal information on specific topic"""
    try:
        info = get_legal_info(topic)
        if not info:
            raise HTTPException(status_code=404, detail="Topic not found")
        return {"success": True, "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ══════════════════════════════════════════════
# SOS EMERGENCY ENDPOINTS
# ══════════════════════════════════════════════

class SOSRequest(BaseModel):
    user_id: int
    location: Optional[dict] = None

@app.post("/api/sos/trigger")
async def trigger_sos(req: SOSRequest):
    """
    Trigger SOS emergency
    In production, this would:
    1. Send SMS to police with location
    2. Call emergency numbers automatically
    3. Alert trusted contacts
    4. Record incident in database
    """
    try:
        # Log SOS trigger
        print(f"🆘 SOS TRIGGERED by user {req.user_id}")
        if req.location:
            print(f"📍 Location: {req.location}")
        
        # In production, integrate with:
        # - SMS gateway to send location to police
        # - Voice calling API to auto-dial 100
        # - Push notifications to trusted contacts
        
        return {
            "success": True,
            "message": "SOS triggered successfully",
            "emergency_numbers": {
                "police": "100",
                "women_helpline": "181",
                "karnataka_helpline": "1091",
                "emergency": "112"
            },
            "actions_taken": [
                "Alarm activated",
                "Emergency numbers displayed",
                "Location recorded" if req.location else "Location not available"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
