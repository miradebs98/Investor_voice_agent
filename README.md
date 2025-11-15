# 🎯 La Pitcheria - AI Voice Agent for Pitch Practice

**Practice your startup pitch with AI-powered investors before facing real VCs.**

La Pitcheria is an AI voice agent that simulates real investor conversations, helping you refine your pitch and prepare for actual investor meetings. Get brutally honest feedback from different investor personas, including top-tier VCs, fashion industry veterans, Formula 1 legends, and more.

## 🎤 What It Does

Practice your pitch in a realistic, conversational setting with AI investors who:
- Ask tough, realistic questions
- Challenge your assumptions
- Test your knowledge of your market
- Evaluate your business model
- Provide honest, constructive feedback

After your conversation, receive an automated pitch report with scores on:
- **Idea** - Quality and clarity of your business concept
- **Market** - Market size and opportunity understanding
- **Clarity** - How well you communicated your vision
- **Moat** - Competitive advantage and defensibility
- **Investment Probability** - Likelihood of getting funded

## ✨ Features

- 🎤 **Real-time Voice Interaction** - Speak naturally, just like a real pitch meeting
- 🗣️ **High-Quality AI Voices** - Powered by ElevenLabs for natural investor responses
- 🤖 **Multiple Investor Personas** - Practice with different types of investors:
  - **Garry Tan** - Top-Tier YC Partner (focuses on unit economics and growth)
  - **Miranda Presley** - Fashion industry veteran (brutally honest, expects perfection)
  - **Flavio Briatore** - Formula 1 legend (demands speed, precision, winning strategies)
  - **Your Grandma** - Loving but honest (asks tough questions with wisdom)
- 💬 **Natural Conversation Flow** - Back-and-forth dialogue, not just Q&A
- 📊 **Automated Pitch Reports** - Get scored feedback after each session
- 🎨 **Modern React UI** - Beautiful, responsive interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with virtual environment
- Node.js 18+ and npm
- API Keys:
  - **ElevenLabs** (get from [elevenlabs.io](https://elevenlabs.io/app/settings/api-keys))
  - **Groq** or **OpenAI** (get from [console.groq.com](https://console.groq.com/) or [platform.openai.com](https://platform.openai.com/api-keys))

### 1. Clone the Repository

```bash
git clone https://github.com/miradebs98/Investor_voice_agent.git
cd Investor_voice_agent
```

### 2. Setup Backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GROQ_API_KEY=your_groq_api_key_here
USE_GROQ=true
ELEVENLABS_VOICE_ID=4NejU5DwQjevnR6mh3mb
EOF

# Start backend server
python run.py
```

Backend runs on: **http://localhost:8000**

### 3. Setup Frontend

```bash
cd pitch-perfect-ai

# Install dependencies
npm install

# Create environment file
echo "VITE_BACKEND_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

Frontend runs on: **http://localhost:8080**

### 4. Start Pitching!

1. Open **http://localhost:8080** in your browser
2. Select an investor persona
3. Click the microphone button
4. Start pitching your startup!

## 📁 Project Structure

```
.
├── backend/                    # FastAPI Backend
│   ├── main.py                 # WebSocket server & API endpoints
│   └── services/
│       ├── vc_agent.py         # Investor personality & LLM integration
│       ├── audio_handler.py    # ElevenLabs TTS integration
│       └── report_generator.py # Automated pitch report generation
├── pitch-perfect-ai/           # React Frontend
│   ├── src/
│   │   ├── pages/              # Landing, SelectPersona, Conversation, Report
│   │   ├── hooks/
│   │   │   └── useVCAgent.ts   # WebSocket connection hook
│   │   └── components/         # UI components
│   └── package.json
├── frontend/                   # Legacy HTML frontend (optional)
├── config.py                   # Configuration & environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 How It Works

1. **Speech Recognition** - Browser's Web Speech API converts your voice to text
2. **WebSocket Communication** - Real-time bidirectional connection between frontend and backend
3. **AI Processing** - Backend sends your pitch to Groq/OpenAI with investor personality prompts
4. **Voice Synthesis** - ElevenLabs converts AI response to natural speech
5. **Report Generation** - After conversation, LLM evaluates your pitch and generates scores

## 🎨 Customization

### Change Investor Personality

Edit `config.py` and modify the `VC_SYSTEM_PROMPT` variable:

```python
VC_SYSTEM_PROMPT = """You are a brutally harsh VC investor...
"""
```

### Add New Investor Personas

1. Add persona image to `pitch-perfect-ai/src/assets/`
2. Update `pitch-perfect-ai/src/pages/SelectPersona.tsx`
3. Update `pitch-perfect-ai/src/pages/Conversation.tsx`

### Change Voice

1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library)
2. Choose a voice or create a custom one
3. Copy the Voice ID
4. Update `ELEVENLABS_VOICE_ID` in your `.env` file

## 🛠️ Troubleshooting

### Backend not starting?
- Check `.env` file has all required API keys
- Verify port 8000 is not in use: `lsof -i :8000`
- Ensure virtual environment is activated

### Frontend not connecting?
- Verify backend is running: `curl http://localhost:8000`
- Check `.env.local` has correct URL: `VITE_BACKEND_URL=http://localhost:8000`
- Check browser console for WebSocket errors

### Audio not playing?
- Browser autoplay restrictions - click microphone button first
- Check browser console for audio errors
- Verify ElevenLabs API key is valid and has credits

### Speech recognition not working?
- Use Chrome, Edge, or Safari (best support)
- Ensure you're on HTTPS or localhost (required for microphone access)
- Grant microphone permissions when prompted

## 💰 API Costs

- **ElevenLabs**: ~$0.12 per minute of generated speech (Creator plan includes 250 free minutes/month)
- **Groq**: Free tier available, very affordable pricing
- **OpenAI**: ~$0.01-0.03 per conversation (GPT-4 Turbo pricing)

## 📚 Documentation

- `QUICK_START.md` - Quick setup guide
- `SETUP.md` - Detailed setup instructions
- `CONNECTION_GUIDE.md` - Frontend-backend integration details

## 🤝 Contributing

Contributions welcome! Feel free to submit issues or pull requests.

## 📄 License

MIT License - Feel free to use and modify for your own projects!

---

**Built with ❤️ using Cursor, ElevenLabs, Groq, and React**

**Practice your pitch. Get funded. 🚀**
