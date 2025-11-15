"""
HeyGen Avatar Integration Handler (OPTIONAL)
Connects the VC voice agent to a HeyGen avatar for real-time streaming.
This is completely optional - the system works perfectly without HeyGen.
To enable: Add HEYGEN_API_KEY and HEYGEN_AVATAR_ID to your .env file
"""
import aiohttp
import base64
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)

class HeyGenHandler:
    def __init__(self):
        self.api_key = getattr(config, 'HEYGEN_API_KEY', None)
        self.avatar_id = getattr(config, 'HEYGEN_AVATAR_ID', None)
        self.base_url = "https://api.heygen.com/v1"
        
        if not self.api_key:
            logger.debug("HEYGEN_API_KEY not set - HeyGen integration disabled (this is fine)")
        if not self.avatar_id:
            logger.debug("HEYGEN_AVATAR_ID not set - HeyGen integration disabled (this is fine)")
    
    async def create_streaming_session(self) -> dict:
        """Create a new HeyGen streaming session"""
        if not self.api_key:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "avatar_id": self.avatar_id,
                    "voice": {
                        "provider": "elevenlabs",
                        "voice_id": config.ELEVENLABS_VOICE_ID
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/streaming.create",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"HeyGen streaming session created: {data.get('session_id')}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"HeyGen API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error creating HeyGen session: {e}")
            return None
    
    async def send_text_to_avatar(self, session_id: str, text: str) -> bool:
        """Send text to HeyGen avatar for real-time speech"""
        if not self.api_key or not session_id:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "session_id": session_id,
                    "text": text
                }
                
                async with session.post(
                    f"{self.base_url}/streaming.say",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"Text sent to HeyGen avatar: {text[:50]}...")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"HeyGen say error: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Error sending text to HeyGen: {e}")
            return False
    
    def get_embed_url(self, session_id: str) -> str:
        """Get the embed URL for the HeyGen avatar"""
        if session_id:
            return f"https://app.heygen.com/streaming?session_id={session_id}"
        return None

