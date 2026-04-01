# Enhanced chat system with legal knowledge base integration
from legal_knowledge import LEGAL_KNOWLEDGE_BASE, get_legal_info
import google.generativeai as genai

class EnhancedChatbot:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def get_response(self, user_message: str, language: str = 'en', history: list = None) -> str:
        """
        Get response with legal knowledge base integration
        This prevents hallucination by grounding responses in verified legal info
        """
        # Extract legal topics from user message
        legal_context = self._extract_legal_context(user_message)
        
        # Build enhanced system prompt with legal facts
        system_prompt = self._build_system_prompt(language, legal_context)
        
        # Call Gemini with grounded context
        try:
            chat = self.model.start_chat(history=history or [])
            response = chat.send_message(
                f"{system_prompt}\n\nUser: {user_message}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                )
            )
            return response.text
        except Exception as e:
            # Fallback to knowledge base only
            return self._fallback_response(user_message, language, legal_context)
    
    def _extract_legal_context(self, message: str) -> dict:
        """Extract relevant legal information based on keywords"""
        message_lower = message.lower()
        context = {}
        
        # Check for relevant legal topics
        if any(word in message_lower for word in ['498', 'cruelty', 'husband', 'abuse', 'beat', 'hit']):
            context['IPC_498A'] = LEGAL_KNOWLEDGE_BASE['IPC_498A']
        
        if any(word in message_lower for word in ['domestic violence', 'protection order', 'pwdva', 'dv act']):
            context['PWDVA_2005'] = LEGAL_KNOWLEDGE_BASE['PWDVA_2005']
        
        if any(word in message_lower for word in ['child', 'minor', 'pocso', 'sexual assault child']):
            context['POCSO_2012'] = LEGAL_KNOWLEDGE_BASE['POCSO_2012']
        
        if any(word in message_lower for word in ['streedhan', 'jewellery', 'dowry', 'property']):
            context['IPC_406'] = LEGAL_KNOWLEDGE_BASE['IPC_406']
        
        if any(word in message_lower for word in ['fir', 'police', 'complaint', 'file case']):
            context['FIR_PROCESS'] = LEGAL_KNOWLEDGE_BASE['FIR_FILING_PROCESS']
        
        if any(word in message_lower for word in ['maintenance', 'alimony', 'money', 'financial']):
            context['MAINTENANCE'] = LEGAL_KNOWLEDGE_BASE['MAINTENANCE_RIGHTS']
        
        if any(word in message_lower for word in ['divorce', 'separation', 'leave husband']):
            context['DIVORCE'] = LEGAL_KNOWLEDGE_BASE['DIVORCE_GROUNDS']
        
        # Always include helplines
        context['HELPLINES'] = LEGAL_KNOWLEDGE_BASE['EMERGENCY_HELPLINES']
        
        return context
    
    def _build_system_prompt(self, language: str, legal_context: dict) -> str:
        """Build system prompt with verified legal facts"""
        base_prompts = {
            'en': """You are SafeVoice, a compassionate AI legal assistant for women in Karnataka, India.

CRITICAL RULES:
1. ONLY use the VERIFIED LEGAL FACTS provided below - DO NOT make up any legal information
2. Be warm, empathetic, and supportive
3. Ask follow-up questions to understand the situation
4. Provide specific, actionable steps
5. Always include relevant helpline numbers

""",
            'kn': """ನೀವು SafeVoice - ಕರ್ನಾಟಕದ ಮಹಿಳೆಯರಿಗೆ ಕಾನೂನು ಸಹಾಯಕ.

ನಿಯಮಗಳು:
1. ಕೆಳಗೆ ನೀಡಿದ ಪರಿಶೀಲಿತ ಕಾನೂನು ಮಾಹಿತಿ ಮಾತ್ರ ಬಳಸಿ
2. ಪ್ರೀತಿ ಮತ್ತು ಸಹಾನುಭೂತಿಯಿಂದ ಮಾತನಾಡಿ
3. ಸ್ಥಿತಿ ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳಲು ಪ್ರಶ್ನೆಗಳು ಕೇಳಿ

""",
            'hi': """आप SafeVoice हैं - कर्नाटक में महिलाओं के लिए कानूनी सहायक।

नियम:
1. केवल नीचे दी गई सत्यापित कानूनी जानकारी का उपयोग करें
2. प्यार और सहानुभूति से बात करें
3. स्थिति समझने के लिए प्रश्न पूछें

""",
            'te': """మీరు SafeVoice - కర్ణాటకలో మహిళలకు చట్టపరమైన సహాయకుడు।

నియమాలు:
1. క్రింద ఇచ్చిన ధృవీకరించిన చట్టపరమైన సమాచారం మాత్రమే ఉపయోగించండి
2. ప్రేమ మరియు సానుభూతితో మాట్లాడండి
3. పరిస్థితి అర్థం చేసుకోవడానికి ప్రశ్నలు అడగండి

"""
        }
        
        prompt = base_prompts.get(language, base_prompts['en'])
        
        # Add verified legal facts
        if legal_context:
            prompt += "\n=== VERIFIED LEGAL FACTS (USE ONLY THESE) ===\n\n"
            for topic, info in legal_context.items():
                if topic == 'HELPLINES':
                    prompt += f"\n**EMERGENCY HELPLINES:**\n"
                    for category, numbers in info.items():
                        if isinstance(numbers, dict):
                            for num, desc in numbers.items():
                                prompt += f"- {num}: {desc}\n"
                else:
                    prompt += f"\n**{info.get('title', topic)}:**\n"
                    if 'key_points' in info:
                        prompt += "Key Points:\n"
                        for point in info['key_points']:
                            prompt += f"- {point}\n"
                    if 'how_to_file' in info:
                        prompt += "\nHow to File:\n"
                        for step in info['how_to_file']:
                            prompt += f"- {step}\n"
                    if 'steps' in info:
                        prompt += "\nSteps:\n"
                        for step in info['steps']:
                            prompt += f"- {step}\n"
        
        return prompt
    
    def _fallback_response(self, message: str, language: str, legal_context: dict) -> str:
        """Fallback response using only knowledge base"""
        responses = {
            'en': "I'm here to help you. Based on your situation, here's what you need to know:\n\n",
            'kn': "ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ. ನಿಮ್ಮ ಸ್ಥಿತಿಯ ಆಧಾರದ ಮೇಲೆ:\n\n",
            'hi': "मैं आपकी मदद के लिए यहाँ हूँ। आपकी स्थिति के आधार पर:\n\n",
            'te': "నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను। మీ పరిస్థితి ఆధారంగా:\n\n"
        }
        
        response = responses.get(language, responses['en'])
        
        # Add relevant legal info
        if 'IPC_498A' in legal_context:
            info = legal_context['IPC_498A']
            response += f"**{info['title']}**\n"
            response += "- " + "\n- ".join(info['key_points'][:3]) + "\n\n"
        
        # Add helplines
        if 'HELPLINES' in legal_context:
            response += "\n**Emergency Helplines:**\n"
            response += "- 100 (Police)\n- 181 (Women Helpline)\n- 1091 (Karnataka Women Helpline)\n"
        
        return response
