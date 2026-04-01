import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import legal knowledge base
from legal_knowledge import LEGAL_KNOWLEDGE_BASE

load_dotenv()

app = FastAPI(title="SafeVoice API", version="2.0.0")

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

# Routes
@app.get("/")
async def serve_auth():
    """Serve authentication page first"""
    auth_path = os.path.join(frontend_path, "auth.html")
    if os.path.exists(auth_path):
        return FileResponse(auth_path)
    return {"message": "Auth page not found"}

@app.get("/app")
async def serve_main_app():
    """Serve main app after authentication"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Main app not found"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "message": "SafeVoice running with legal knowledge base",
        "model": "knowledge-base-v1"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat endpoint with legal knowledge base
    Gives accurate responses based on verified legal information
    """
    message = req.message.lower()
    lang = req.language or "en"
    
    response_parts = []
    
    # Check for IPC 498A keywords
    if any(word in message for word in ['498', 'husband', 'cruelty', 'beat', 'hit', 'abuse', 'violence', 'hurt']):
        info = LEGAL_KNOWLEDGE_BASE.get('IPC_498A', {})
        if info:
            response_parts.append(f"**{info['title']}**\n\n")
            response_parts.append("This law protects you. Here's what you need to know:\n\n")
            response_parts.append("**Key Points:**\n")
            for i, point in enumerate(info['key_points'], 1):
                response_parts.append(f"{i}. {point}\n")
            response_parts.append("\n**How to File a Complaint:**\n")
            for i, step in enumerate(info['how_to_file'][:4], 1):
                response_parts.append(f"{i}. {step}\n")
    
    # Check for PWDVA keywords
    elif any(word in message for word in ['domestic violence', 'protection', 'pwdva', 'dv act', 'protection order']):
        info = LEGAL_KNOWLEDGE_BASE.get('PWDVA_2005', {})
        if info:
            response_parts.append(f"**{info['title']}**\n\n")
            response_parts.append("**Key Points:**\n")
            for i, point in enumerate(info['key_points'], 1):
                response_parts.append(f"{i}. {point}\n")
            response_parts.append("\n**Orders You Can Get:**\n")
            for i, order in enumerate(info['orders_available'], 1):
                response_parts.append(f"{i}. {order}\n")
    
    # Check for FIR filing
    elif any(word in message for word in ['fir', 'file', 'complaint', 'police', 'report']):
        info = LEGAL_KNOWLEDGE_BASE.get('FIR_FILING_PROCESS', {})
        if info:
            response_parts.append("**How to File an FIR:**\n\n")
            for i, step in enumerate(info['steps'][:6], 1):
                response_parts.append(f"{i}. {step}\n")
            response_parts.append("\n**Your Rights:**\n")
            for right in info['rights'][:4]:
                response_parts.append(f"• {right}\n")
    
    # Check for POCSO
    elif any(word in message for word in ['child', 'minor', 'pocso', 'under 18']):
        info = LEGAL_KNOWLEDGE_BASE.get('POCSO_2012', {})
        if info:
            response_parts.append(f"**{info['title']}**\n\n")
            response_parts.append("**Key Points:**\n")
            for point in info['key_points']:
                response_parts.append(f"• {point}\n")
            response_parts.append("\n**How to Report:**\n")
            for step in info['how_to_report'][:4]:
                response_parts.append(f"• {step}\n")
    
    # Check for streedhan/property
    elif any(word in message for word in ['streedhan', 'jewellery', 'jewelry', 'property', 'dowry', 'gifts']):
        info = LEGAL_KNOWLEDGE_BASE.get('IPC_406', {})
        if info:
            response_parts.append(f"**{info['title']}**\n\n")
            response_parts.append("**What is Streedhan:**\n")
            for item in info['what_is_streedhan']:
                response_parts.append(f"• {item}\n")
            response_parts.append("\n**How to Recover:**\n")
            for step in info['how_to_recover']:
                response_parts.append(f"• {step}\n")
    
    # Check for shelter/help
    elif any(word in message for word in ['shelter', 'help', 'safe', 'escape', 'leave']):
        response_parts.append("**Immediate Help Available:**\n\n")
        response_parts.append("1. **One Stop Centre**: 7827170170\n")
        response_parts.append("   - Medical aid\n")
        response_parts.append("   - Police assistance\n")
        response_parts.append("   - Legal aid\n")
        response_parts.append("   - Shelter\n\n")
        response_parts.append("2. **Women Helpline**: 181 (24/7)\n")
        response_parts.append("3. **Karnataka Helpline**: 1091\n")
        response_parts.append("4. **Police Emergency**: 100\n")
    
    # Default response with helplines
    else:
        response_parts.append("I'm here to help you. You are brave for reaching out. 💜\n\n")
        response_parts.append("I can help you with:\n")
        response_parts.append("• **IPC 498A** - Protection from cruelty by husband/relatives\n")
        response_parts.append("• **PWDVA** - Domestic violence protection orders\n")
        response_parts.append("• **FIR Filing** - How to file a police complaint\n")
        response_parts.append("• **POCSO** - Child protection laws\n")
        response_parts.append("• **Streedhan** - Recovering your property/jewellery\n")
        response_parts.append("• **Shelter & Support** - Finding safe places\n\n")
        response_parts.append("Please tell me what's happening, and I'll guide you with the right legal information.\n")
    
    # Always add emergency helplines
    helplines = LEGAL_KNOWLEDGE_BASE.get('EMERGENCY_HELPLINES', {})
    if helplines and response_parts:
        response_parts.append("\n**📞 Emergency Helplines:**\n")
        national = helplines.get('national', {})
        response_parts.append(f"• **100** - {national.get('100', 'Police Emergency')}\n")
        response_parts.append(f"• **181** - {national.get('181', 'Women Helpline')}\n")
        response_parts.append(f"• **1091** - {national.get('1091', 'Karnataka Women Helpline')}\n")
    
    reply = "".join(response_parts)
    
    return ChatResponse(
        reply=reply,
        source="legal_knowledge_base"
    )

@app.get("/api/helplines")
async def helplines():
    helplines_data = LEGAL_KNOWLEDGE_BASE.get('EMERGENCY_HELPLINES', {})
    national = helplines_data.get('national', {})
    karnataka = helplines_data.get('karnataka_specific', {})
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
