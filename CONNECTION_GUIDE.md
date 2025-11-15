# 🔗 Connection Guide: Backend ↔ Frontend Integration

This guide explains how to connect the **FastAPI Backend** (VC Investor Voice Agent) with the **React Frontend** (Pitch Perfect AI).

## 📁 Project Structure

```
Hackaton/
├── backend/              # FastAPI Backend (Port 8000)
│   ├── main.py          # WebSocket server
│   └── services/        # VC Agent, Audio Handler
│
└── pitch-perfect-ai/    # React Frontend (Port 8080)
    └── src/
        ├── pages/
        │   └── Conversation.tsx  # Needs backend connection
        └── hooks/
            └── useVCAgent.ts      # WebSocket hook (to be created)
```

## 🚀 Quick Start

### 1. Start Backend

```bash
cd /Users/mira/Desktop/Mira/Hackaton
python run.py
# Backend runs on http://localhost:8000
```

### 2. Start Frontend

```bash
cd /Users/mira/Desktop/Mira/Hackaton/pitch-perfect-ai
npm install  # First time only
npm run dev
# Frontend runs on http://localhost:8080
```

### 3. Environment Variables

Create `.env.local` in `pitch-perfect-ai/`:

```env
VITE_BACKEND_URL=http://localhost:8000
```

## 🔌 WebSocket Connection

### Backend Endpoint
- **URL**: `ws://localhost:8000/ws` (or `wss://` for HTTPS)
- **Protocol**: WebSocket
- **CORS**: Already configured to allow all origins

### Message Format

#### **Send to Backend:**
```json
// Send user transcript
{
  "type": "text",
  "text": "My startup is..."
}

// Reset conversation
{
  "type": "reset"
}
```

#### **Receive from Backend:**
```json
// VC audio response
{
  "type": "audio",
  "data": "base64_encoded_audio_mp3",
  "text": "Alright, pitch me. What's your startup?",
  "avatar_image_url": "https://..."
}

// User message confirmation
{
  "type": "user_message",
  "text": "My startup is..."
}

// Error
{
  "type": "text_error",
  "text": "Error message"
}
```

## 🛠️ Integration Steps

### Step 1: Create WebSocket Hook

File: `pitch-perfect-ai/src/hooks/useVCAgent.ts`

This hook handles:
- WebSocket connection to backend
- Speech recognition (browser API)
- Audio playback
- Message state management

### Step 2: Update Conversation Component

File: `pitch-perfect-ai/src/pages/Conversation.tsx`

Replace mock behavior with real backend connection using the hook.

### Step 3: Add Environment Variable

File: `pitch-perfect-ai/.env.local`
```env
VITE_BACKEND_URL=http://localhost:8000
```

## 📝 Implementation Details

### WebSocket Connection Flow

1. **Connect**: Frontend connects to `ws://localhost:8000/ws`
2. **Welcome**: Backend sends welcome message with audio
3. **User Speaks**: Frontend uses browser Speech Recognition
4. **Send Transcript**: Frontend sends text to backend via WebSocket
5. **VC Responds**: Backend processes, generates response, converts to speech
6. **Receive Audio**: Frontend receives base64 audio and plays it
7. **Repeat**: Continue conversation loop

### Speech Recognition

- Uses browser's `SpeechRecognition` API (Chrome/Edge only)
- Sends transcript to backend when user stops speaking
- Handles errors gracefully

### Audio Playback

- Receives base64-encoded MP3 audio from backend
- Creates `Audio` object` with `data:audio/mpeg;base64:...`
- Plays automatically when received
- Handles browser autoplay restrictions

## 🐛 Troubleshooting

### WebSocket Connection Fails
- ✅ Check backend is running: `curl http://localhost:8000`
- ✅ Check backend logs for errors
- ✅ Verify `VITE_BACKEND_URL` in `.env.local`
- ✅ Check browser console for WebSocket errors

### CORS Errors
- ✅ Backend already has `allow_origins=["*"]` - should work
- ✅ If issues, check backend `main.py` CORS settings

### Audio Not Playing
- ✅ Browser autoplay restrictions - user must interact first
- ✅ Check browser console for audio errors
- ✅ Verify base64 audio data is valid

### Speech Recognition Not Working
- ✅ Only works in Chrome/Edge browsers
- ✅ Requires microphone permissions
- ✅ Check browser console for errors

## 🎯 Next Steps

1. ✅ Create `useVCAgent.ts` hook
2. ✅ Update `Conversation.tsx` to use hook
3. ✅ Test connection
4. ✅ Add error handling
5. ✅ Add reconnection logic
6. ✅ Style improvements

## 📚 Files to Modify

- `pitch-perfect-ai/src/hooks/useVCAgent.ts` - **NEW** - WebSocket hook
- `pitch-perfect-ai/src/pages/Conversation.tsx` - **UPDATE** - Use hook
- `pitch-perfect-ai/.env.local` - **NEW** - Environment variables

## 🔐 Backend Requirements

The backend needs these environment variables (already set up):
- `ELEVENLABS_API_KEY` - For text-to-speech
- `GROQ_API_KEY` - For LLM (or `OPENAI_API_KEY`)
- `USE_GROQ=true` - To use Groq instead of OpenAI
- `FREE_AVATAR_IMAGE_URL` - Optional avatar image

See `config.py` for all configuration options.

