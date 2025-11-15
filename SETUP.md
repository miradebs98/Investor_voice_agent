# Quick Setup Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Create .env File

Copy the template below and create a `.env` file in the project root:

```bash
# ElevenLabs API Key
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom Voice ID
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

**Where to get your keys:**
- **ElevenLabs**: https://elevenlabs.io/app/settings/api-keys
- **OpenAI**: https://platform.openai.com/api-keys

## Step 3: Run the Server

```bash
python run.py
```

## Step 4: Open in Browser

Go to: `http://localhost:8000`

## That's it! 🎉

You should now see the VC Investor interface. Click "Start Recording" and begin your pitch!

---

**Troubleshooting:**
- Make sure both API keys are set correctly
- Use Chrome or Edge for best browser compatibility
- Allow microphone access when prompted

