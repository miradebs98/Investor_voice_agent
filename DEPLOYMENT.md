# 🚀 Deployment Guide: La Pitcheria

This guide will help you deploy both the frontend and backend so anyone can use your pitch practice app.

## 📋 Overview

You need to deploy:
1. **Frontend** (React/Vite) - Public website users access
2. **Backend** (FastAPI) - API server that handles AI conversations

## Option 1: Quick Deployment (Recommended)

### Frontend: Vercel (Free & Easy)

Vercel is perfect for React/Vite apps and offers free hosting.

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Deploy Frontend
```bash
cd pitch-perfect-ai
vercel
```

Follow the prompts:
- Link to existing project? **No** (first time)
- Project name: **la-pitcheria** (or your choice)
- Directory: **./** (current directory)
- Override settings? **No**

#### Step 3: Set Environment Variable
After deployment, go to Vercel dashboard:
1. Go to: https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Name**: `VITE_BACKEND_URL`
   - **Value**: `https://your-backend-url.com` (see backend deployment below)
   - **Environment**: Production, Preview, Development
5. Click **Save**
6. Go to **Deployments** → Click **Redeploy** (to apply env var)

### Backend: Railway / Render / Fly.io

#### Option A: Railway (Easiest)

1. Go to: https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository: `miradebs98/Investor_voice_agent`
5. Railway will auto-detect Python
6. Add environment variables in Railway dashboard:
   ```
   ELEVENLABS_API_KEY=your_key
   GROQ_API_KEY=your_key
   USE_GROQ=true
   ELEVENLABS_VOICE_ID=4NejU5DwQjevnR6mh3mb
   PORT=8000
   ```
7. Railway will give you a URL like: `https://your-app.railway.app`
8. Update frontend `VITE_BACKEND_URL` to this URL

#### Option B: Render (Free Tier)

1. Go to: https://render.com
2. Sign up
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo
5. Settings:
   - **Name**: `la-pitcheria-backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Port**: `8000`
6. Add environment variables (same as Railway)
7. Deploy!

#### Option C: Fly.io (Good for WebSockets)

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. In project root: `fly launch`
4. Follow prompts
5. Add secrets: `fly secrets set ELEVENLABS_API_KEY=xxx GROQ_API_KEY=xxx`
6. Deploy: `fly deploy`

## Option 2: Manual Deployment

### Frontend: Netlify

1. Go to: https://app.netlify.com
2. Drag & drop `pitch-perfect-ai/dist` folder (after building)
3. Or connect GitHub repo
4. Build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Add environment variable: `VITE_BACKEND_URL`

### Backend: DigitalOcean / AWS / Google Cloud

Similar process - deploy Python app with environment variables.

## 🔧 Important Configuration

### CORS Settings

Your backend already has CORS enabled for all origins. If you want to restrict it:

Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### WebSocket Support

Make sure your backend hosting supports WebSockets:
- ✅ Railway: Supports WebSockets
- ✅ Render: Supports WebSockets (with upgrade)
- ✅ Fly.io: Excellent WebSocket support
- ⚠️ Some free tiers may have limitations

## 📝 Deployment Checklist

- [ ] Deploy backend to Railway/Render/Fly.io
- [ ] Get backend URL (e.g., `https://your-backend.railway.app`)
- [ ] Deploy frontend to Vercel
- [ ] Set `VITE_BACKEND_URL` environment variable in Vercel
- [ ] Test WebSocket connection
- [ ] Test full conversation flow
- [ ] Share your frontend URL!

## 🎯 Quick Commands

### Build Frontend Locally (for testing)
```bash
cd pitch-perfect-ai
npm run build
# Output in dist/ folder
```

### Test Production Build
```bash
cd pitch-perfect-ai
npm run build
npm run preview
# Test at http://localhost:4173
```

## 🔗 After Deployment

Your users will access:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.railway.app` (not directly accessed by users)

The frontend automatically connects to your backend via WebSocket and HTTP API.

## 🆘 Troubleshooting

### Frontend can't connect to backend
- Check `VITE_BACKEND_URL` is set correctly
- Verify backend is running and accessible
- Check CORS settings in backend
- Check browser console for errors

### WebSocket connection fails
- Ensure backend hosting supports WebSockets
- Check backend logs for connection errors
- Verify backend URL uses `wss://` (not `ws://`) for HTTPS

### Environment variables not working
- Rebuild/redeploy after adding env vars
- Check variable names match exactly (case-sensitive)
- Verify environment scope (Production/Preview/Development)

---

**Need help?** Check the deployment platform's documentation or open an issue.

