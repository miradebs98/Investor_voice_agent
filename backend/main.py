from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import asyncio
import logging
from typing import Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.vc_agent import VCAgent
from backend.services.audio_handler import AudioHandler
from backend.services.heygen_handler import HeyGenHandler
from backend.services.did_handler import DIDHandler
from backend.services.report_generator import ReportGenerator
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VC Investor Voice Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
active_connections: Dict[str, Dict] = {}

# Serve static files
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def read_root():
    return FileResponse(str(frontend_path / "index.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connection_id = id(websocket)
    
    try:
        # Initialize services for this connection
        vc_agent = VCAgent()
        audio_handler = AudioHandler()
        
        # Initialize avatar handler (D-ID or HeyGen - optional)
        # NOTE: Free animated avatar with lip sync is always available if FREE_AVATAR_IMAGE_URL is set
        avatar_handler = None
        avatar_session = None
        avatar_embed_url = None
        avatar_type = None
        
        # Skip D-ID and HeyGen - use free animated avatar instead
        # (Uncomment below if you want to use D-ID/HeyGen)
        # # Try D-ID first (free tier available)
        # try:
        #     did_handler = DIDHandler()
        #     if did_handler.api_key and did_handler.avatar_id:
        #         logger.info("D-ID credentials found - attempting to create streaming session")
        #         avatar_session = await did_handler.create_streaming_session()
        #         if avatar_session:
        #             avatar_embed_url = did_handler.get_embed_url(avatar_session.get("session_id") or avatar_session.get("agent_id"))
        #             avatar_handler = did_handler
        #             avatar_type = "did"
        #             logger.info("D-ID avatar session created successfully")
        #         else:
        #             logger.warning("D-ID session creation failed - using free avatar")
        #     else:
        #         logger.info("D-ID not configured - using free avatar")
        # except Exception as e:
        #     logger.warning(f"D-ID initialization failed - using free avatar: {e}")
        
        # Free animated avatar is always used (no API needed)
        logger.info("Using free animated avatar with Web Audio lip sync")
        
        active_connections[connection_id] = {
            "vc_agent": vc_agent,
            "audio_handler": audio_handler,
            "avatar_handler": avatar_handler,
            "avatar_session": avatar_session,
            "avatar_type": avatar_type,
            "websocket": websocket
        }
        
        # Send welcome message
        welcome_text = "Alright, pitch me. What's your startup?"
        welcome_audio = await audio_handler.text_to_speech(welcome_text)
        
        # Get free avatar image URL if configured (no API needed)
        free_avatar_url = getattr(config, 'FREE_AVATAR_IMAGE_URL', None)
        
        # Send welcome message to client (with free avatar image URL)
        await websocket.send_json({
            "type": "audio",
            "data": welcome_audio,
            "text": welcome_text,
            "avatar_image_url": free_avatar_url  # Free animated avatar with lip sync
        })
        
        # Skip sending to D-ID/HeyGen - free avatar handles everything client-side
        
        # Main conversation loop
        logger.info("Entering main conversation loop, waiting for messages...")
        while True:
            try:
                data = await websocket.receive()
                logger.info(f"📨 Received WebSocket data - type: {type(data)}, keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}, content: {str(data)[:200]}")
            except RuntimeError as e:
                # WebSocket disconnected
                if "disconnect" in str(e).lower():
                    logger.info("WebSocket disconnected")
                    break
                raise
            except Exception as e:
                logger.error(f"Error receiving WebSocket data: {e}", exc_info=True)
                break
            
            # Check if this is a disconnect message
            if isinstance(data, dict) and data.get("type") == "websocket.disconnect":
                logger.info("Received disconnect message")
                break
            
            if "text" in data:
                # Text message received
                try:
                    message = json.loads(data["text"])
                    logger.info(f"Parsed message: {message}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {data.get('text')} - {e}")
                    continue
                
                if message.get("type") == "text":
                    # Text transcript received (from browser Speech Recognition)
                    transcript = message.get("text", "").strip()
                    
                    if transcript:
                        logger.info(f"User said: {transcript}")
                        
                        try:
                            # Check if WebSocket is still connected before sending
                            if websocket.client_state.name != "CONNECTED":
                                logger.warning("WebSocket not connected, skipping message processing")
                                break
                            
                            # Add user message to UI
                            try:
                                await websocket.send_json({
                                    "type": "user_message",
                                    "text": transcript
                                })
                            except Exception as send_err:
                                logger.warning(f"Failed to send user message: {send_err}")
                                break
                            
                            # Get VC response
                            logger.info("Getting VC response...")
                            vc_response = await vc_agent.get_response(transcript)
                            logger.info(f"VC response: {vc_response}")
                            
                            if not vc_response:
                                raise ValueError("No response generated from VC agent")
                            
                            # Convert to speech
                            logger.info("Converting to speech...")
                            vc_audio = await audio_handler.text_to_speech(vc_response)
                            logger.info("Speech conversion complete")
                            
                            # Check connection again before sending response
                            if websocket.client_state.name != "CONNECTED":
                                logger.warning("WebSocket disconnected during processing, skipping response")
                                break
                            
                            # Get free avatar image URL if configured
                            free_avatar_url = getattr(config, 'FREE_AVATAR_IMAGE_URL', None)
                            
                            # Send back to client (free avatar handles lip sync client-side)
                            try:
                                await websocket.send_json({
                                    "type": "audio",
                                    "data": vc_audio,
                                    "text": vc_response,
                                    "avatar_image_url": free_avatar_url  # Free animated avatar with Web Audio lip sync
                                })
                                logger.info("Response sent to client")
                            except Exception as send_err:
                                logger.warning(f"Failed to send response: {send_err}")
                                break
                            
                        except Exception as e:
                            logger.error(f"Error processing message: {e}", exc_info=True)
                            # Send error message to client
                            error_message = "Sorry, I'm having technical difficulties. Let me try again - what's your startup about?"
                            try:
                                error_audio = await audio_handler.text_to_speech(error_message)
                                await websocket.send_json({
                                    "type": "audio",
                                    "data": error_audio,
                                    "text": error_message
                                })
                            except:
                                # If TTS also fails, just send text
                                await websocket.send_json({
                                    "type": "text_error",
                                    "text": error_message
                                })
                
                elif message.get("type") == "reset":
                    # Reset conversation
                    vc_agent.reset_conversation()
                    welcome_text = "Alright, pitch me. What's your startup?"
                    welcome_audio = await audio_handler.text_to_speech(welcome_text)
                    
                    await websocket.send_json({
                        "type": "audio",
                        "data": welcome_audio,
                        "text": welcome_text
                    })
                    
    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected normally")
    except RuntimeError as e:
        if "disconnect" in str(e).lower():
            logger.info(f"Client {connection_id} disconnected")
        else:
            logger.error(f"WebSocket runtime error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in websocket: {e}", exc_info=True)
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]
            logger.debug(f"Cleaned up connection {connection_id}")

@app.post("/api/generate-report")
async def generate_report_endpoint(request: Request):
    """Generate pitch report from conversation history"""
    try:
        data = await request.json()
        connection_id = data.get("connection_id")
        conversation_history = data.get("conversation_history", [])
        
        # Try to use existing connection's agent if available
        if connection_id and connection_id in active_connections:
            vc_agent = active_connections[connection_id]["vc_agent"]
            # Use conversation history from the agent
            conversation_history = vc_agent.conversation_history
        else:
            # Create new agent for report generation
            vc_agent = VCAgent()
            # Use provided conversation history
            if not conversation_history:
                logger.warning("No conversation history provided and no active connection")
                return {
                    "success": False,
                    "error": "No conversation history available",
                    "report": ReportGenerator(None, None, False)._get_default_report()
                }
        
        # Create report generator with agent's LLM
        report_generator = ReportGenerator(
            vc_agent.llm_client,
            vc_agent.llm_model,
            vc_agent.is_groq
        )
        
        # Generate report
        report = await report_generator.generate_report(conversation_history)
        
        logger.info(f"✅ Report generated successfully: {report.get('investment_probability')}% probability")
        
        return {"success": True, "report": report}
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        # Return default report on error
        default_report = ReportGenerator(None, None, False)._get_default_report()
        return {
            "success": False,
            "error": str(e),
            "report": default_report
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

