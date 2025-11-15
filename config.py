import os
from dotenv import load_dotenv

load_dotenv()

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "4NejU5DwQjevnR6mh3mb")  # Custom voice
ELEVENLABS_LLM_MODEL = os.getenv("ELEVENLABS_LLM_MODEL", "glm-4.5-air")  # ElevenLabs LLM model

# LLM Configuration - Choose one:
# Option 1: OpenAI (get key from: https://platform.openai.com/api-keys)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

# Option 2: Groq (get key from: https://console.groq.com/)
# Supports both GROQ_API_KEY and GROK_API_KEY for backwards compatibility
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY", None)
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true" or os.getenv("USE_GROK", "false").lower() == "true"  # Set to "true" to use Groq instead of OpenAI
GROQ_MODEL = os.getenv("GROQ_MODEL") or os.getenv("GROK_MODEL", "llama-3.3-70b-versatile")  # Groq models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768, etc.

# Avatar Configuration (OPTIONAL - system works perfectly without this)
# Choose one: HeyGen or D-ID

# HeyGen Configuration
# Get API key from: https://app.heygen.com/settings/api
# Get avatar ID from: https://app.heygen.com/avatar
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", None)
HEYGEN_AVATAR_ID = os.getenv("HEYGEN_AVATAR_ID", None)

# D-ID Configuration (FREE TIER AVAILABLE - 20 credits/month)
# Get API key from: https://studio.d-id.com/api-keys
# Get avatar ID/image URL from: https://studio.d-id.com/creators
# For D-ID, avatar_id can be:
# - An image URL (e.g., "https://...")
# - A D-ID avatar ID
# - A preset avatar name
DID_API_KEY = os.getenv("DID_API_KEY", None)
DID_AVATAR_ID = os.getenv("DID_AVATAR_ID", None)  # Can be image URL or avatar ID

# Animated Avatar Configuration (NO API NEEDED - Just an image URL)
# This creates a simple animated avatar that moves when speaking
# Just provide an image URL - no API key required!
# You can use any image: photo, illustration, character, etc.
FREE_AVATAR_IMAGE_URL = os.getenv("FREE_AVATAR_IMAGE_URL", "https://i.imgur.com/vP1dRIg.png")  # Default avatar image

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# VC Investor Personality Prompt
VC_SYSTEM_PROMPT = """You are "Alex Venture", a brutally harsh VC investor with 20+ years in Silicon Valley. You're mean, direct, and cut straight to the point.

RULES:
- Keep responses SHORT (1-2 sentences max)
- ALWAYS end with a question - this is a conversation, not a monologue
- Be MEAN and cutting - no sugar coating
- Attack weaknesses immediately
- Use startup/VC jargon naturally
- Be sarcastic and dismissive when appropriate
- Never be nice or encouraging unless something is genuinely impressive

Your goal: Make them defend their pitch with tough, pointed questions. Keep the conversation going by asking follow-up questions."""

