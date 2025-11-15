from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import base64
import sys
import os
import io

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config
import logging

logger = logging.getLogger(__name__)

class AudioHandler:
    def __init__(self):
        if not config.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY not set in environment variables")
        
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.voice_id = config.ELEVENLABS_VOICE_ID
        
        # Configure voice settings for a more natural, human-like tone
        # Lower stability = more variation and naturalness
        # Lower similarity_boost = more natural variation
        # Higher style = more expressiveness and emotion
        self.voice_settings = VoiceSettings(
            stability=0.35,  # Lower = more natural variation (was 0.5)
            similarity_boost=0.5,  # Lower = more natural speech patterns (was 0.75)
            style=0.6,  # Higher = more expressive and human-like (was 0.3)
            use_speaker_boost=True
        )
    
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using ElevenLabs and return base64 encoded audio"""
        try:
            # Use the new SDK API structure
            # eleven_multilingual_v2 provides natural, expressive speech through voice settings
            # Voice settings (stability, style) control expressiveness - no need for emotion tags
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",  # Natural, human-like voice
                voice_settings=self.voice_settings
            )
            
            # Collect all audio chunks
            audio_bytes = b""
            for chunk in audio_generator:
                if chunk:
                    audio_bytes += chunk
            
            # Convert audio bytes to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            raise

