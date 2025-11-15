# 🚀 Quick Start: Connect Frontend to Backend

## Prerequisites

- Python 3.8+ with virtual environment
- Node.js 18+ and npm
- Backend API keys in `.env` file

## Step 1: Setup Backend

```bash
cd /Users/mira/Desktop/Mira/Hackaton

# Activate virtual environment (if not already)
source venv/bin/activate

# Start backend server
python run.py
```

Backend will run on: **http://localhost:8000**

## Step 2: Setup Frontend

```bash
cd /Users/mira/Desktop/Mira/Hackaton/pitch-perfect-ai

# Install dependencies (first time only)
npm install

# Create environment file
echo "VITE_BACKEND_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

Frontend will run on: **http://localhost:8080**

## Step 3: Test Connection

1. Open browser: http://localhost:8080
2. Navigate to conversation page
3. Check browser console for: `✅ Connected to backend`
4. Click microphone button to start recording
5. Speak your pitch!

## Troubleshooting

### Backend not starting?
- Check `.env` file has all required API keys
- Check port 8000 is not in use: `lsof -i :8000`

### Frontend not connecting?
- Verify backend is running: `curl http://localhost:8000`
- Check `.env.local` has correct URL
- Check browser console for WebSocket errors

### Audio not playing?
- Browser autoplay restrictions - click microphone first
- Check browser console for audio errors

## Files Created

- ✅ `CONNECTION_GUIDE.md` - Full integration documentation
- ✅ `pitch-perfect-ai/src/hooks/useVCAgent.ts` - WebSocket hook
- ✅ `pitch-perfect-ai/src/pages/Conversation.tsx` - Updated to use backend
- ✅ `pitch-perfect-ai/.env.local.example` - Environment template

## Next Steps

1. Test the connection
2. Customize the VC personality in `config.py`
3. Add more personas if needed
4. Deploy when ready!

