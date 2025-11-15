# 🚀 Quick Deploy Guide - La Pitcheria

## Step 1: Deploy Backend (Railway - Easiest)

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **Click "New Project"** → **"Deploy from GitHub repo"**
4. **Select**: `miradebs98/Investor_voice_agent`
5. **Railway auto-detects Python** - click "Deploy Now"
6. **Add Environment Variables** (Settings → Variables):
   ```
   ELEVENLABS_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   USE_GROQ=true
   ELEVENLABS_VOICE_ID=4NejU5DwQjevnR6mh3mb
   PORT=8000
   ```
7. **Get your backend URL**: Railway gives you a URL like `https://your-app.railway.app`
8. **Copy this URL** - you'll need it for frontend!

## Step 2: Deploy Frontend (Vercel - Free & Fast)

### Option A: Using Vercel CLI (Recommended)

```bash
cd pitch-perfect-ai
npm install -g vercel
vercel
```

Follow prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name:** la-pitcheria
- **Directory:** ./
- **Override settings?** No

After deployment:
1. Go to Vercel dashboard: https://vercel.com/dashboard
2. Select your project
3. **Settings** → **Environment Variables**
4. Add:
   - **Name**: `VITE_BACKEND_URL`
   - **Value**: `https://your-backend.railway.app` (from Step 1)
   - **Environments**: Production, Preview, Development
5. **Save**
6. **Deployments** → Click **"Redeploy"** (latest deployment)

### Option B: Using Vercel Website

1. Go to: https://vercel.com/new
2. **Import Git Repository**: Select `miradebs98/Investor_voice_agent`
3. **Root Directory**: `pitch-perfect-ai`
4. **Framework Preset**: Vite
5. **Build Command**: `npm run build`
6. **Output Directory**: `dist`
7. **Environment Variables**:
   - `VITE_BACKEND_URL` = `https://your-backend.railway.app`
8. **Deploy!**

## Step 3: Test It!

1. Open your Vercel URL (e.g., `https://la-pitcheria.vercel.app`)
2. Select an investor persona
3. Click microphone
4. Start pitching!

## ✅ Done!

Your app is now live! Share the Vercel URL with anyone.

---

**Backend URL**: `https://your-backend.railway.app`
**Frontend URL**: `https://la-pitcheria.vercel.app` (or your custom domain)
