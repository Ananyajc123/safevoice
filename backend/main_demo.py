import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import hashlib
import secrets

# Import legal knowledge base and database
from legal_knowledge import LEGAL_KNOWLEDGE_BASE
from database import Database

load_dotenv()

app = FastAPI(title="SafeVoice API - Demo", version="2.0.0")
db = Database()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend path
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    reply: str
    source: str

class SignupRequest(BaseModel):
    disguise_key: str
    face_image: str

class LoginRequest(BaseModel):
    disguise_key: str
    face_image: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    session_token: Optional[str] = None

class FIRRequest(BaseModel):
    user_id: str
    complainant_name: str
    complainant_phone: str
    complainant_address: str
    accused_details: str
    incident_details: str
    laws_invoked: str

class FIRResponse(BaseModel):
    success: bool
    message: str
    case_id: Optional[str] = None

# Routes
@app.get("/")
async def serve_auth():
    """Serve authentication page first"""
    auth_path = os.path.join(frontend_path, "auth_simple.html")
    print(f"🔍 Looking for auth_simple.html at: {auth_path}")
    print(f"🔍 File exists: {os.path.exists(auth_path)}")
    
    if os.path.exists(auth_path):
        print("✅ Serving auth_simple.html")
        return FileResponse(
            auth_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    print("❌ Auth page not found")
    return {"message": "Auth page not found", "path": auth_path}

@app.get("/auth")
async def serve_auth_explicit():
    """Explicit auth route"""
    auth_path = os.path.join(frontend_path, "auth_simple.html")
    if os.path.exists(auth_path):
        return FileResponse(
            auth_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {"message": "Auth page not found"}

@app.get("/app")
async def serve_main_app():
    """Serve main app after authentication"""
    index_path = os.path.join(frontend_path, "index_main_app.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Main app not found"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "SafeVoice running - Demo mode (no face recognition)",
        "model": "knowledge-base-v1"
    }

# SIMPLIFIED AUTH - No face recognition required for demo
@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(req: SignupRequest):
    """
    Simplified signup for demo - accepts all women
    """
    try:
        print(f"\n🔍 SIGNUP REQUEST:")
        print(f"   Disguise key length: {len(req.disguise_key) if req.disguise_key else 0}")
        print(f"   Face image provided: {'Yes' if req.face_image else 'No'}")
        
        # Validate disguise key
        if not req.disguise_key or len(req.disguise_key) < 4:
            print("   ❌ Disguise key too short")
            return AuthResponse(
                success=False,
                message="Disguise key must be at least 4 characters"
            )
        
        # For demo: Just check if face image exists
        if not req.face_image or len(req.face_image) < 100:
            print("   ❌ No face image provided")
            return AuthResponse(
                success=False,
                message="Please capture your photo first"
            )
        
        # Demo mode: Always allow signup (assume female)
        # In production, this would use face recognition
        print(f"   ✅ Demo signup - Allowing access (women's safety app)")
        
        # Create user in database
        # Use a simple face encoding for demo
        fake_face_encoding = hashlib.sha256(req.face_image[:100].encode()).hexdigest()
        
        print(f"   📝 Creating user in database...")
        user_id = db.create_user(
            disguise_key=req.disguise_key,
            face_encoding=fake_face_encoding,
            gender='female'  # Demo: assume female
        )
        
        print(f"   ✅ User created with ID: {user_id}")
        
        if user_id is None:
            return AuthResponse(
                success=False,
                message="This disguise key is already registered. Please use a different key or try logging in."
            )
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        return AuthResponse(
            success=True,
            message="✅ Account created successfully! Welcome to SafeVoice. (Demo mode - face recognition disabled)",
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
    Simplified login for demo
    """
    try:
        # Verify disguise key
        user = db.verify_user(req.disguise_key)
        
        if not user:
            return AuthResponse(
                success=False,
                message="Invalid disguise key. Please check and try again, or sign up if you're new."
            )
        
        # Demo mode: Skip face verification
        print(f"✅ Demo login - User {user['id']} logged in")
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        return AuthResponse(
            success=True,
            message=f"✅ Welcome back! (Demo mode - face verification disabled)",
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
    """Check if user exists"""
    try:
        user = db.verify_user(req.disguise_key)
        
        if user:
            return {
                "exists": True,
                "face_match": True,  # Demo: always match
                "message": "User found. Redirecting to login..."
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
    """
    Enhanced chat endpoint with:
    - Multi-language support (responds in same language as query)
    - Conversational style with follow-up questions
    - Specific guidance based on situation
    """
    message = req.message.lower()
    original_message = req.message  # Keep original for language detection
    lang = req.language or "en"
    
    # Language-specific responses
    LANG_RESPONSES = {
        'en': {
            'greeting': "I'm here to help you. You are brave for reaching out. 💜\n\n",
            'tell_more': "Can you tell me more about what's happening? ",
            'how_long': "How long has this been going on? ",
            'are_you_safe': "Are you safe right now? ",
            'any_children': "Do you have children? ",
            'want_to_leave': "Do you want to leave or get protection while staying? ",
            'have_evidence': "Do you have any evidence (photos, messages, witnesses)? ",
            'filed_complaint': "Have you filed any complaint before? ",
            'emergency': "📞 **Emergency - Call Now:**\n• **100** - Police\n• **181** - Women Helpline\n• **1091** - Karnataka Women Helpline\n",
            'i_understand': "I understand this is difficult. ",
            'you_have_rights': "You have legal rights and protection. ",
            'lets_help': "Let me help you step by step. "
        },
        'kn': {
            'greeting': "ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ. ನೀವು ಧೈರ್ಯಶಾಲಿ. 💜\n\n",
            'tell_more': "ಏನಾಗುತ್ತಿದೆ ಎಂದು ಹೆಚ್ಚು ಹೇಳಬಹುದೇ? ",
            'how_long': "ಇದು ಎಷ್ಟು ದಿನದಿಂದ ನಡೆಯುತ್ತಿದೆ? ",
            'are_you_safe': "ನೀವು ಈಗ ಸುರಕ್ಷಿತವಾಗಿದ್ದೀರಾ? ",
            'any_children': "ನಿಮಗೆ ಮಕ್ಕಳಿದ್ದಾರೆಯೇ? ",
            'want_to_leave': "ನೀವು ಮನೆ ಬಿಡಲು ಬಯಸುತ್ತೀರಾ ಅಥವಾ ಇದ್ದಲ್ಲೇ ರಕ್ಷಣೆ ಬೇಕೇ? ",
            'have_evidence': "ನಿಮ್ಮ ಬಳಿ ಯಾವುದೇ ಪುರಾವೆ ಇದೆಯೇ (ಫೋಟೋ, ಸಂದೇಶ, ಸಾಕ್ಷಿಗಳು)? ",
            'filed_complaint': "ನೀವು ಮೊದಲು ಯಾವುದೇ ದೂರು ಸಲ್ಲಿಸಿದ್ದೀರಾ? ",
            'emergency': "📞 **ತುರ್ತು - ಈಗ ಕರೆ ಮಾಡಿ:**\n• **100** - ಪೊಲೀಸ್\n• **181** - ಮಹಿಳಾ ಸಹಾಯವಾಣಿ\n• **1091** - ಕರ್ನಾಟಕ ಮಹಿಳಾ ಸಹಾಯವಾಣಿ\n",
            'i_understand': "ಇದು ಕಷ್ಟ ಎಂದು ನನಗೆ ಅರ್ಥವಾಗುತ್ತದೆ. ",
            'you_have_rights': "ನಿಮಗೆ ಕಾನೂನು ಹಕ್ಕುಗಳು ಮತ್ತು ರಕ್ಷಣೆ ಇದೆ. ",
            'lets_help': "ನಾನು ನಿಮಗೆ ಹಂತ ಹಂತವಾಗಿ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. "
        },
        'hi': {
            'greeting': "मैं आपकी मदद के लिए यहाँ हूँ। आप बहादुर हैं। 💜\n\n",
            'tell_more': "क्या आप मुझे बता सकती हैं कि क्या हो रहा है? ",
            'how_long': "यह कितने समय से हो रहा है? ",
            'are_you_safe': "क्या आप अभी सुरक्षित हैं? ",
            'any_children': "क्या आपके बच्चे हैं? ",
            'want_to_leave': "क्या आप घर छोड़ना चाहती हैं या वहीं रहकर सुरक्षा चाहती हैं? ",
            'have_evidence': "क्या आपके पास कोई सबूत है (फोटो, संदेश, गवाह)? ",
            'filed_complaint': "क्या आपने पहले कोई शिकायत दर्ज की है? ",
            'emergency': "📞 **आपातकाल - अभी कॉल करें:**\n• **100** - पुलिस\n• **181** - महिला हेल्पलाइन\n• **1091** - कर्नाटक महिला हेल्पलाइन\n",
            'i_understand': "मैं समझती हूँ कि यह मुश्किल है। ",
            'you_have_rights': "आपके पास कानूनी अधिकार और सुरक्षा है। ",
            'lets_help': "मैं आपकी कदम दर कदम मदद करूँगी। "
        },
        'te': {
            'greeting': "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీరు ధైర్యవంతులు. 💜\n\n",
            'tell_more': "ఏమి జరుగుతుందో మరింత చెప్పగలరా? ",
            'how_long': "ఇది ఎంతకాలం నుండి జరుగుతోంది? ",
            'are_you_safe': "మీరు ఇప్పుడు సురక్షితంగా ఉన్నారా? ",
            'any_children': "మీకు పిల్లలు ఉన్నారా? ",
            'want_to_leave': "మీరు ఇల్లు వదిలి వెళ్లాలనుకుంటున్నారా లేదా అక్కడే ఉండి రక్షణ కావాలా? ",
            'have_evidence': "మీ దగ్గర ఏదైనా సాక్ష్యం ఉందా (ఫోటోలు, సందేశాలు, సాక్షులు)? ",
            'filed_complaint': "మీరు ఇంతకు ముందు ఏదైనా ఫిర్యాదు చేశారా? ",
            'emergency': "📞 **అత్యవసరం - ఇప్పుడే కాల్ చేయండి:**\n• **100** - పోలీస్\n• **181** - మహిళా హెల్ప్‌లైన్\n• **1091** - కర్ణాటక మహిళా హెల్ప్‌లైన్\n",
            'i_understand': "ఇది కష్టమని నాకు అర్థమవుతోంది. ",
            'you_have_rights': "మీకు చట్టపరమైన హక్కులు మరియు రక్షణ ఉన్నాయి. ",
            'lets_help': "నేను మీకు దశలవారీగా సహాయం చేస్తాను. "
        }
    }
    
    # Detect language from message if not specified
    if any(char in original_message for char in 'ಅಆಇಈಉಊಋಎಏಐಒಓಔಕಖಗಘಙಚಛಜಝಞಟಠಡಢಣತಥದಧನಪಫಬಭಮಯರಲವಶಷಸಹಳೞ'):
        lang = 'kn'
    elif any(char in original_message for char in 'अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'):
        lang = 'hi'
    elif any(char in original_message for char in 'అఆఇఈఉఊఋఎఏఐఒఓఔకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళ'):
        lang = 'te'
    
    responses = LANG_RESPONSES.get(lang, LANG_RESPONSES['en'])
    response_parts = []
    
    # Check for immediate danger
    if any(word in message for word in ['danger', 'emergency', 'now', 'help me', 'urgent', 'ಈಗ', 'ತುರ್ತು', 'अभी', 'आपातकाल', 'ఇప్పుడు', 'అత్యవసరం']):
        response_parts.append(responses['emergency'])
        response_parts.append(responses['are_you_safe'])
        response_parts.append("\n" + responses['i_understand'])
        
    # Check for physical abuse
    elif any(word in message for word in ['beat', 'hit', 'hurt', 'violence', 'assault', 'ಹೊಡೆ', 'ಹಿಂಸೆ', 'मारना', 'हिंसा', 'కొట్ట', 'హింస']):
        response_parts.append(responses['i_understand'])
        response_parts.append(responses['you_have_rights'])
        response_parts.append("\n\n**IPC 498A - Protection from Cruelty**\n")
        response_parts.append("This law protects you from physical and mental cruelty by husband or his relatives.\n\n")
        response_parts.append("**Punishment:** Up to 3 years imprisonment + fine (Non-bailable)\n\n")
        response_parts.append(responses['tell_more'])
        response_parts.append(responses['how_long'])
        response_parts.append(responses['have_evidence'])
        response_parts.append("\n\n" + responses['emergency'])
        
    # Check for dowry harassment
    elif any(word in message for word in ['dowry', 'money', 'demand', 'ವರದಕ್ಷಿಣೆ', 'ಹಣ', 'दहेज', 'पैसा', 'కట్నం', 'డబ్బు']):
        response_parts.append(responses['greeting'])
        response_parts.append("**Dowry Prohibition Act & IPC 498A**\n\n")
        response_parts.append("Demanding dowry is a criminal offence. You are protected by law.\n\n")
        response_parts.append("**What you can do:**\n")
        response_parts.append("1. File FIR under IPC 498A (cruelty) and Dowry Prohibition Act\n")
        response_parts.append("2. Police must register your complaint\n")
        response_parts.append("3. Accused can be arrested without bail\n\n")
        response_parts.append(responses['tell_more'])
        response_parts.append("What are they demanding? ")
        response_parts.append(responses['how_long'])
        response_parts.append("\n\n" + responses['emergency'])
        
    # Check for streedhan
    elif any(word in message for word in ['jewellery', 'jewelry', 'gold', 'streedhan', 'property', 'gifts', 'ಆಭರಣ', 'ಸ್ತ್ರೀಧನ', 'गहने', 'स्त्रीधन', 'ఆభరణాలు', 'స్త్రీధనం']):
        response_parts.append(responses['greeting'])
        response_parts.append("**IPC 406 - Streedhan Protection**\n\n")
        response_parts.append("Your jewellery, gifts, and property given at marriage belong to YOU. Withholding them is criminal breach of trust.\n\n")
        response_parts.append("**What is Streedhan:**\n")
        response_parts.append("• Jewellery given at marriage\n")
        response_parts.append("• Gifts from parents/relatives\n")
        response_parts.append("• Money and property in your name\n\n")
        response_parts.append("**How to recover:**\n")
        response_parts.append("1. Send legal notice demanding return\n")
        response_parts.append("2. File complaint under IPC 406\n")
        response_parts.append("3. File PWDVA application for monetary relief\n\n")
        response_parts.append("What items are being withheld? ")
        response_parts.append("Do you have any receipts or photos? ")
        response_parts.append("\n\n" + responses['emergency'])
        
    # Check for wanting to leave/escape
    elif any(word in message for word in ['leave', 'escape', 'run away', 'shelter', 'safe place', 'ಹೊರಡು', 'ಆಶ್ರಯ', 'छोड़ना', 'भागना', 'आश्रय', 'వదిలి', 'తప్పించుకో', 'ఆశ్రయం']):
        response_parts.append(responses['greeting'])
        response_parts.append("**Safe Exit Planning**\n\n")
        response_parts.append("I'll help you plan a safe exit. Here's what you need:\n\n")
        response_parts.append("**Immediate shelter options:**\n")
        response_parts.append("• One Stop Centre: 7827170170 (Free shelter, medical, legal aid)\n")
        response_parts.append("• Women's shelter homes (call 181 for nearest)\n")
        response_parts.append("• Police station (they must provide protection)\n\n")
        response_parts.append("**What to take:**\n")
        response_parts.append("• ID proof (Aadhaar, PAN)\n")
        response_parts.append("• Bank documents\n")
        response_parts.append("• Marriage certificate\n")
        response_parts.append("• Evidence (photos, messages)\n")
        response_parts.append("• Children's documents\n\n")
        response_parts.append(responses['are_you_safe'])
        response_parts.append(responses['any_children'])
        response_parts.append("Do you have a trusted friend or family member? ")
        response_parts.append("\n\n" + responses['emergency'])
        
    # Check for FIR filing
    elif any(word in message for word in ['fir', 'complaint', 'police', 'report', 'ದೂರು', 'ಪೊಲೀಸ್', 'शिकायत', 'पुलिस', 'ఫిర్యాదు', 'పోలీస్']):
        response_parts.append(responses['lets_help'])
        response_parts.append("\n\n**How to File FIR:**\n\n")
        response_parts.append("1. Go to nearest police station (any station, not just your area)\n")
        response_parts.append("2. Ask for women police officer (your right)\n")
        response_parts.append("3. Give written complaint - police CANNOT refuse\n")
        response_parts.append("4. Get free FIR copy\n")
        response_parts.append("5. Police will investigate and can arrest without bail\n\n")
        response_parts.append("**Your Rights:**\n")
        response_parts.append("• Police must register FIR\n")
        response_parts.append("• You can file in any police station\n")
        response_parts.append("• FIR copy is free\n")
        response_parts.append("• You can file online through our app\n\n")
        response_parts.append("What happened? ")
        response_parts.append(responses['how_long'])
        response_parts.append(responses['have_evidence'])
        response_parts.append("\n\n" + responses['emergency'])
        
    # Check for protection order
    elif any(word in message for word in ['protection', 'order', 'pwdva', 'domestic violence', 'ರಕ್ಷಣೆ', 'ಆದೇಶ', 'सुरक्षा', 'आदेश', 'రక్షణ', 'ఆర్డర్']):
        response_parts.append(responses['you_have_rights'])
        response_parts.append("\n\n**PWDVA 2005 - Protection Orders**\n\n")
        response_parts.append("You can get emergency protection within 24 hours!\n\n")
        response_parts.append("**Types of Orders:**\n")
        response_parts.append("1. **Protection Order** - He cannot abuse you\n")
        response_parts.append("2. **Residence Order** - You can stay in your home\n")
        response_parts.append("3. **Monetary Relief** - Maintenance and compensation\n")
        response_parts.append("4. **Custody Order** - Children stay with you\n\n")
        response_parts.append("**How to apply:**\n")
        response_parts.append("• Go to Magistrate court\n")
        response_parts.append("• Or contact Protection Officer (call 181)\n")
        response_parts.append("• Free legal aid available\n\n")
        response_parts.append(responses['want_to_leave'])
        response_parts.append(responses['any_children'])
        response_parts.append("\n\n" + responses['emergency'])
        
    # Default conversational response
    else:
        response_parts.append(responses['greeting'])
        response_parts.append(responses['tell_more'])
        response_parts.append("\n\nI can help you with:\n\n")
        response_parts.append("**Legal Protection:**\n")
        response_parts.append("• IPC 498A - Cruelty by husband/relatives\n")
        response_parts.append("• PWDVA - Protection orders (24 hours)\n")
        response_parts.append("• IPC 406 - Recovering your jewellery/property\n")
        response_parts.append("• FIR filing - Step by step guidance\n\n")
        response_parts.append("**Immediate Help:**\n")
        response_parts.append("• Safe shelter and escape planning\n")
        response_parts.append("• Emergency helplines\n")
        response_parts.append("• Free legal aid\n\n")
        response_parts.append("Please describe your situation, and I'll guide you with specific legal steps.\n")
        response_parts.append("\n" + responses['emergency'])
    
    reply = "".join(response_parts)
    
    return ChatResponse(
        reply=reply,
        source="legal_knowledge_base"
    )

@app.get("/api/helplines")
async def helplines():
    helplines_data = LEGAL_KNOWLEDGE_BASE.get('EMERGENCY_HELPLINES', {})
    national = helplines_data.get('national', {})
    
    result = []
    for num, desc in national.items():
        result.append({
            "name": desc.split(' - ')[0] if ' - ' in desc else desc,
            "number": num,
            "desc": desc.split(' - ')[1] if ' - ' in desc else desc,
            "tag": "24/7",
            "icon": "📞"
        })
    
    return {"helplines": result}

@app.post("/api/fir/file")
async def file_fir(req: FIRRequest):
    """
    File FIR online - creates a case record in database
    """
    try:
        # Generate unique case ID
        import uuid
        from datetime import datetime
        
        case_id = f"FIR-KA-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Save to database
        db = DatabaseManager()
        fir_id = db.file_fir(
            user_id=req.user_id,
            complainant_name=req.complainant_name,
            complainant_phone=req.complainant_phone,
            complainant_address=req.complainant_address,
            accused_details=req.accused_details,
            incident_details=req.incident_details,
            laws_invoked=req.laws_invoked,
            case_id=case_id
        )
        
        if fir_id:
            return FIRResponse(
                success=True,
                message="FIR filed successfully",
                case_id=case_id
            )
        else:
            return FIRResponse(
                success=False,
                message="Failed to file FIR"
            )
    except Exception as e:
        print(f"Error filing FIR: {e}")
        return FIRResponse(
            success=False,
            message=f"Error: {str(e)}"
        )

@app.get("/api/fir/{user_id}")
async def get_user_firs(user_id: str):
    """
    Get all FIRs filed by a user
    """
    try:
        db = DatabaseManager()
        firs = db.get_user_firs(user_id)
        return {"firs": firs}
    except Exception as e:
        print(f"Error getting FIRs: {e}")
        return {"firs": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
