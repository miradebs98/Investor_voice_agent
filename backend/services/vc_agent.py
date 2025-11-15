from elevenlabs.client import ElevenLabs
from typing import List, Dict, Optional
import sys
import os
import json
import aiohttp

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
import logging

logger = logging.getLogger(__name__)

class VCAgent:
    def __init__(self):
        if not config.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY not set in environment variables")
        
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.api_key = config.ELEVENLABS_API_KEY
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": config.VC_SYSTEM_PROMPT}
        ]
        # Use ElevenLabs' built-in LLM (GLM-4.5-Air is a good default) - for fallback only
        self.elevenlabs_llm_model = getattr(config, 'ELEVENLABS_LLM_MODEL', 'glm-4.5-air')
        
        # Initialize LLM client (OpenAI or Groq)
        self.llm_client = None
        self.llm_model = None
        # Check for both GROQ and GROK (for backwards compatibility with .env file)
        self.use_groq = getattr(config, 'USE_GROQ', False) or getattr(config, 'USE_GROK', False)
        self.is_groq = False  # Track if using Groq SDK vs OpenAI SDK
        
        # Get API key (try GROQ first, then GROK for backwards compatibility)
        groq_api_key = getattr(config, 'GROQ_API_KEY', None) or getattr(config, 'GROK_API_KEY', None)
        
        if self.use_groq and groq_api_key:
            try:
                from groq import Groq
                self.llm_client = Groq(api_key=groq_api_key)
                self.llm_model = getattr(config, 'GROQ_MODEL', "llama-3.3-70b-versatile")
                self.is_groq = True
                logger.info(f"✅ Groq client initialized with model: {self.llm_model}")
            except ImportError:
                logger.warning("Groq package not available. Install with: pip install groq")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # Only use OpenAI if Groq is not enabled
        if not self.use_groq and config.OPENAI_API_KEY and not self.llm_client:
            try:
                import openai
                self.llm_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
                self.llm_model = "gpt-4o-mini"
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI package not available, skipping LLM")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = [
            {"role": "system", "content": config.VC_SYSTEM_PROMPT}
        ]
    
    async def _try_elevenlabs_llm(self, messages: List[Dict]) -> Optional[str]:
        """Try to use ElevenLabs LLM via HTTP API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # Try the LLM endpoint (this may vary based on ElevenLabs API structure)
                payload = {
                    "model": self.elevenlabs_llm_model,
                    "messages": messages,
                    "temperature": 0.9,
                    "max_tokens": 80  # Shorter responses
                }
                
                # Try different possible endpoints
                endpoints = [
                    f"https://api.elevenlabs.io/v1/llm/chat",
                    f"https://api.elevenlabs.io/v1/chat/completions",
                    f"https://api.elevenlabs.io/v1/conversational-ai/chat"
                ]
                
                for endpoint in endpoints:
                    try:
                        async with session.post(endpoint, headers=headers, json=payload) as response:
                            if response.status == 200:
                                data = await response.json()
                                # Try different response structures
                                if "choices" in data:
                                    content = data["choices"][0].get("message", {}).get("content", "").strip()
                                elif "message" in data:
                                    content = data["message"].strip()
                                elif "text" in data:
                                    content = data["text"].strip()
                                else:
                                    content = str(data).strip()
                                
                                if content:
                                    return content
                    except Exception as e:
                        logger.debug(f"Tried {endpoint}, error: {e}")
                        continue
        except Exception as e:
            logger.debug(f"ElevenLabs LLM API attempt failed: {e}")
        
        return None
    
    async def _try_llm_api(self, messages: List[Dict]) -> Optional[str]:
        """Primary LLM - OpenAI or Groq"""
        if not self.llm_client:
            provider = "Groq" if self.use_groq else "OpenAI"
            logger.warning(f"{provider} client not initialized - check API key in .env")
            return None
        
        try:
            if self.is_groq:
                # Use Groq SDK - try multiple models if one fails
                models_to_try = [
                    self.llm_model,  # Try configured model first
                    "llama-3.3-70b-versatile",  # Latest 70B model
                    "llama-3.1-8b-instant",  # Fast 8B model
                    "mixtral-8x7b-32768",  # Alternative model
                    "llama-3.1-70b-versatile"  # Old model (might still work)
                ]
                
                # Remove duplicates while preserving order
                models_to_try = list(dict.fromkeys(models_to_try))
                
                for model in models_to_try:
                    try:
                        logger.info(f"Calling Groq API with model: {model}")
                        response = self.llm_client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0.9,
                            max_tokens=80
                        )
                        result = response.choices[0].message.content.strip()
                        logger.info(f"✅ Groq response generated (model: {model}): {result[:50]}...")
                        # Update self.llm_model to the working model for future calls
                        self.llm_model = model
                        return result
                    except Exception as model_error:
                        error_msg = str(model_error)
                        # Check if it's a model-specific error (decommissioned, not found, etc.)
                        if "decommissioned" in error_msg.lower() or "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                            logger.warning(f"Model {model} not available: {error_msg[:100]}")
                            continue  # Try next model
                        else:
                            # Other error (rate limit, auth, etc.) - don't try other models
                            raise model_error
                
                # If all models failed, raise an error
                raise Exception("All Groq models failed")
            else:
                # Use OpenAI SDK
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=messages,
                    temperature=0.9,
                    max_tokens=80
                )
                result = response.choices[0].message.content.strip()
                logger.info(f"✅ OpenAI response generated: {result[:50]}...")
                return result
            
        except Exception as e:
            provider = "Groq" if self.use_groq else "OpenAI"
            error_details = str(e)
            
            # Get detailed error information
            if hasattr(e, 'body'):
                try:
                    import json
                    error_body = json.loads(e.body) if isinstance(e.body, str) else e.body
                    error_details = f"{error_details} - API Response: {error_body}"
                except:
                    error_details = f"{error_details} - Body: {str(e.body)}"
            
            logger.error(f"❌ {provider} API failed: {error_details}")
            
            # No fallback - stick to Groq only if USE_GROQ is true
            if self.use_groq:
                logger.error("Groq API failed. Check your API key and model name. No OpenAI fallback will be used.")
            
            return None
    
    async def get_response(self, user_input: str) -> str:
        """Get VC's response to user input"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Format messages for API
        messages = []
        for msg in self.conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Try primary LLM first (OpenAI or Groq)
        vc_response = await self._try_llm_api(messages)
        
        # Fallback to ElevenLabs LLM if primary LLM doesn't work
        if not vc_response:
            logger.info("Primary LLM not available, trying ElevenLabs LLM")
            vc_response = await self._try_elevenlabs_llm(messages)
        
        # Final fallback: improved human-like responses
        if not vc_response:
            logger.warning("Both LLM options failed, using fallback responses")
            vc_response = self._get_fallback_response(user_input)
        
        # Note: Emotion tags like [sarcastic] are not supported by eleven_multilingual_v2
        # The voice settings (stability, style) already provide natural expressiveness
        # So we just use the response as-is
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": vc_response
        })
        
        return vc_response
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Fallback response when LLM is unavailable - more human and varied"""
        import random
        user_lower = user_input.lower()
        
        # Short, mean responses that always end with questions
        if any(word in user_lower for word in ["market", "size", "tam", "sam", "target market"]):
            responses = [
                "Huge market? Everyone says that. What's your actual TAM?",
                "Who's your customer? 'Small businesses' isn't a market.",
                "Give me numbers. What's the addressable market?",
                "Market size means nothing if you can't capture it. How will you?"
            ]
        elif any(word in user_lower for word in ["revenue", "money", "funding", "raise", "paying", "customers", "users"]):
            responses = [
                "Show me revenue. Not projections, actual numbers. What is it?",
                "How many paying customers? Free users don't count.",
                "What's your MRR? Don't tell me, show me.",
                "Are people actually paying you? Prove it."
            ]
        elif any(word in user_lower for word in ["team", "founder", "co-founder", "we", "i'm", "i am"]):
            responses = [
                "Why should I bet on you? What's your track record?",
                "What have you built before? I need proof you can execute.",
                "Ideas are worthless. What makes you capable?",
                "I invest in teams, not ideas. Why are you the right people?"
            ]
        elif any(word in user_lower for word in ["competitor", "competition", "competitive", "better than", "vs"]):
            responses = [
                "What's your moat? Why won't someone copy you tomorrow?",
                "Everyone has competitors. What makes you different?",
                "I've seen this before. Why will you win?",
                "What's your unfair advantage? Be specific."
            ]
        elif any(word in user_lower for word in ["problem", "solving", "help", "need"]):
            responses = [
                "Is this a real pain point or just nice-to-have? How do you know?",
                "Will people actually pay to solve this? Prove it.",
                "Who has this problem? Be specific.",
                "How much does this problem cost them? In dollars."
            ]
        elif any(word in user_lower for word in ["app", "platform", "software", "tool", "product"]):
            responses = [
                "I've seen a thousand apps. What makes yours different?",
                "How do you make money? That's what matters.",
                "Do people want it? Show me proof.",
                "How will you get customers? Distribution is everything."
            ]
        else:
            # Short, mean generic responses
            responses = [
                "Too vague. What problem are you solving and who pays?",
                "Be specific. Who's your customer?",
                "What makes you different? I've heard this before.",
                "How do you make money? That's the only question that matters.",
                "Give me something concrete. What's your traction?",
                "Who pays? How much? When?",
                "Why should I care? What's your value prop?"
            ]
        
        return random.choice(responses)

