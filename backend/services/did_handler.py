"""
D-ID Avatar Integration Handler (OPTIONAL)
Connects the VC voice agent to a D-ID avatar for real-time streaming.
This is completely optional - the system works perfectly without D-ID.
To enable: Add DID_API_KEY and DID_AVATAR_ID to your .env file
"""
import aiohttp
import base64
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config

logger = logging.getLogger(__name__)

class DIDHandler:
    def __init__(self):
        self.api_key = getattr(config, 'DID_API_KEY', None)
        self.avatar_id = getattr(config, 'DID_AVATAR_ID', None)
        self.base_url = "https://api.d-id.com"
        
        if not self.api_key:
            logger.debug("DID_API_KEY not set - D-ID integration disabled (this is fine)")
        if not self.avatar_id:
            logger.debug("DID_AVATAR_ID not set - D-ID integration disabled (this is fine)")
    
    def _get_auth_header(self):
        """Get properly formatted Authorization header for D-ID API"""
        # D-ID API key format: username:password (needs base64 encoding for Basic auth)
        # If it contains ':', it's username:password format - encode it
        if ':' in self.api_key:
            # Format: username:password - encode it for Basic auth
            encoded = base64.b64encode(self.api_key.encode()).decode()
            return encoded
        else:
            # Use as-is (might be already encoded or direct API key)
            return self.api_key
    
    async def create_streaming_session(self) -> dict:
        """Create a new D-ID streaming session using the official streaming API"""
        if not self.api_key or not self.avatar_id:
            return None
        
        try:
            auth_header = self._get_auth_header()
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/json"
                }
                
                # D-ID Streaming API - use /talks/streams endpoint (official method)
                # Based on: https://github.com/de-id/live-streaming-demo
                payload = {
                    "source_url": self.avatar_id,  # Image URL or avatar ID
                    "config": {
                        "fluent": True,
                        "pad_audio": 0.0,
                        "stitch": True
                    }
                }
                
                # Try the official streaming endpoint first
                async with session.post(
                    f"{self.base_url}/talks/streams",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        stream_id = data.get("id") or data.get("stream_id")
                        logger.info(f"✅ D-ID streaming session created: {stream_id}")
                        return {"stream_id": stream_id, "session_id": stream_id, "data": data}
                    else:
                        error_text = await response.text()
                        logger.warning(f"D-ID streaming endpoint error: {response.status} - {error_text}")
                        # Try Agents API as fallback
                        return await self._try_agents_api(session, headers)
        except Exception as e:
            logger.error(f"Error creating D-ID session: {e}")
            return None
    
    async def _try_agents_api(self, session, headers):
        """Try D-ID Agents API as fallback"""
        try:
            payload = {
                "source_url": self.avatar_id,
                "config": {
                    "fluent": True,
                    "pad_audio": 0.0
                }
            }
            
            async with session.post(
                f"{self.base_url}/agents",
                headers=headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    agent_id = data.get("id") or data.get("agent_id")
                    logger.info(f"D-ID agent created: {agent_id}")
                    return {"agent_id": agent_id, "session_id": agent_id}
                else:
                    error_text = await response.text()
                    logger.error(f"D-ID Agents API error: {response.status} - {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error trying Agents API: {e}")
            return None
    
    async def send_text_to_avatar(self, session_id: str, text: str) -> bool:
        """Send text to D-ID avatar for real-time speech using streaming API"""
        if not self.api_key or not session_id:
            return False
        
        try:
            auth_header = self._get_auth_header()
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/json"
                }
                
                # D-ID Streaming API - send text to stream
                # Based on official demo: https://github.com/de-id/live-streaming-demo
                payload = {
                    "script": {
                        "type": "text",
                        "input": text,
                        "subtitles": False
                    }
                }
                
                # Try streaming endpoint first (official method)
                async with session.post(
                    f"{self.base_url}/talks/streams/{session_id}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"✅ Text sent to D-ID stream: {text[:50]}...")
                        return True
                    else:
                        error_text = await response.text()
                        logger.warning(f"D-ID stream error: {response.status} - {error_text}")
                        # Try Agents API as fallback
                        return await self._send_to_agent(session, headers, session_id, text)
        except Exception as e:
            logger.error(f"Error sending text to D-ID: {e}")
            return False
    
    async def _send_to_agent(self, session, headers, agent_id: str, text: str) -> bool:
        """Try sending to Agents API as fallback"""
        try:
            payload = {"text": text}
            async with session.post(
                f"{self.base_url}/agents/{agent_id}/chat",
                headers=headers,
                json=payload
            ) as response:
                if response.status in [200, 201]:
                    logger.info(f"Text sent to D-ID agent: {text[:50]}...")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"D-ID agent error: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Error sending to D-ID agent: {e}")
            return False
    
    
    def get_embed_url(self, session_id: str) -> str:
        """Get the embed URL for the D-ID avatar"""
        if session_id:
            # D-ID Streaming API embed URL
            # Based on official demo: https://github.com/de-id/live-streaming-demo
            # Format: https://d-id.com/streams/{stream_id}
            return f"https://d-id.com/streams/{session_id}"
        return None

