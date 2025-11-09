# Complete Deployment Guide - Backend + Frontend

## 🎯 Overview

For your app to work for ALL users, you need **TWO separate deployments**:

```
1. Backend (Render) → Processes predictions with Claude AI
2. Frontend (Vercel) → Shows UI and calls backend API
```

**Both must be deployed for the app to work!**

---

## 🏗️ Architecture Diagram

```
User's Browser
     ↓
[Frontend on Vercel]
https://poly-predictor.vercel.app
     ↓ (Makes API calls)
[Backend on Render]
https://poly-predictor-backend.onrender.com
     ↓ (Calls external APIs)
[Claude AI, Google, NewsAPI, Yahoo Finance]
```

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ Code pushed to GitHub (branch: data-nikhil)
- ✅ Render account (free at render.com)
- ✅ Vercel account (free at vercel.com)
- ✅ API keys ready:
  - Anthropic Claude API
  - NewsAPI
  - Google Custom Search API
  - Google Custom Search Engine ID

---

## 🚀 Part 1: Deploy Backend on Render

### Why Render for Backend?
- ✅ Supports Python/Flask
- ✅ Free tier available
- ✅ Easy to configure
- ✅ Can handle Claude API calls

### Step 1.1: Create Render Account

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render

### Step 1.2: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select: `Claude-Hackathon`
4. **Configure settings:**

```
Name:           poly-predictor-backend
Region:         Oregon (or closest to you)
Branch:         data-nikhil
Root Directory: backend              ⚠️ IMPORTANT!
Runtime:        Python 3
Build Command:  pip install -r requirements.txt
Start Command:  gunicorn app:app
```

### Step 1.3: Add Environment Variables

Click **"Advanced"** and add these environment variables:

```
ANTHROPIC_API_KEY     = [your_key_here]
NEWS_API_KEY          = [your_key_here]
GOOGLE_API_KEY        = [your_key_here]
GOOGLE_CSE_ID         = [your_cse_id_here]
FLASK_ENV             = production
```

**⚠️ Important:** Copy keys without quotes or extra spaces!

### Step 1.4: Deploy Backend

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Watch the logs for any errors
4. Note your backend URL:
   ```
   https://poly-predictor-backend.onrender.com
   ```

### Step 1.5: Test Backend

Visit these URLs to verify:

```bash
# Health check
https://poly-predictor-backend.onrender.com/api/health
Expected: {"status": "healthy"}

# If health check works, backend is ready! ✅
```

**⚠️ First load may take 30-60 seconds (cold start on free tier)**

---

## 🎨 Part 2: Deploy Frontend on Vercel

### Why Vercel for Frontend?
- ✅ Optimized for React
- ✅ Global CDN (super fast)
- ✅ Free tier is excellent
- ✅ No cold starts

### Step 2.1: Create Vercel Account

1. Go to https://vercel.com
2. Click "Sign Up"
3. Sign up with GitHub
4. Authorize Vercel

### Step 2.2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Select `Claude-Hackathon` from GitHub
3. **Configure project:**

```
Project Name:     poly-predictor
Framework Preset: Create React App    (auto-detected)
Root Directory:   frontend            ⚠️ CRITICAL!

Build Settings (usually auto-detected):
├─ Build Command:    npm run build
├─ Output Directory: build
└─ Install Command:  npm install
```

### Step 2.3: Add Environment Variable

**CRITICAL STEP** - Tell frontend where backend is:

Click **"Environment Variables"** and add:

```
Name:  REACT_APP_API_URL
Value: https://poly-predictor-backend.onrender.com

⚠️ Replace with YOUR actual backend URL from Render!
```

### Step 2.4: Deploy Frontend

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Get your frontend URL:
   ```
   https://poly-predictor.vercel.app
   ```

### Step 2.5: Test Frontend

1. Visit: `https://poly-predictor.vercel.app`
2. You should see your beautiful UI
3. Try a prediction: "Will Bitcoin reach $100k?"
4. Should get results from backend ✅

---

## 🔗 How They Work Together

### **Local Development (Your Computer):**

```bash
# Backend runs on:
http://localhost:5001

# Frontend runs on:
http://localhost:3000

# Frontend calls localhost backend
REACT_APP_API_URL not set → uses localhost:5001
```

### **Production (Deployed):**

```bash
# Backend runs on:
https://poly-predictor-backend.onrender.com

# Frontend runs on:
https://poly-predictor.vercel.app

# Frontend calls deployed backend
REACT_APP_API_URL set → uses Render backend
```

### **For Other Users:**

```
1. User visits Vercel URL
2. Vercel serves React app (HTML/CSS/JS)
3. User enters query and clicks submit
4. Frontend makes API call to Render backend
5. Render backend:
   ├─ Scrapes Google
   ├─ Calls NewsAPI
   ├─ Gets Yahoo Finance data
   ├─ Calls Claude AI
   └─ Returns prediction
6. Frontend displays results
```

---

## ✅ Verification Checklist

After deploying both, verify everything works:

### Backend Tests:

- [ ] Health endpoint works:
  ```
  https://your-backend.onrender.com/api/health
  Returns: {"status": "healthy"}
  ```

- [ ] No errors in Render logs
- [ ] Environment variables are set correctly
- [ ] Backend URL noted for frontend config

### Frontend Tests:

- [ ] Site loads without 404 error
- [ ] UI displays correctly
- [ ] Can enter a query
- [ ] Submit button works
- [ ] Loading spinner appears
- [ ] Results display with prediction
- [ ] Confidence score shows
- [ ] Data quality metrics visible

### Integration Tests:

- [ ] Frontend can reach backend (no CORS errors)
- [ ] Predictions complete successfully
- [ ] Backend logs show requests from frontend
- [ ] No timeout errors
- [ ] All 4 data sources work (Google, NewsAPI, Yahoo, MarketWatch)

---

## 🐛 Troubleshooting

### Issue 1: Frontend Can't Reach Backend

**Symptoms:**
- "Network Error" in frontend
- CORS errors in browser console
- Predictions never complete

**Solutions:**

1. **Check environment variable:**
   ```
   Vercel → Project → Settings → Environment Variables
   Verify REACT_APP_API_URL is set correctly
   ```

2. **Verify backend is running:**
   ```
   Visit: https://your-backend-url.onrender.com/api/health
   Should return: {"status": "healthy"}
   ```

3. **Check CORS in backend:**
   ```python
   # In backend/app.py, should have:
   CORS(app, resources={
       r"/api/*": {
           "origins": "*",  # ✅ Allows all origins
   ```

4. **Redeploy both services:**
   ```
   Render: Deployments → Redeploy
   Vercel: Deployments → Redeploy
   ```

---

### Issue 2: Backend Returns 500 Error

**Symptoms:**
- Predictions fail with "Server Error"
- Render logs show errors

**Solutions:**

1. **Check API keys:**
   ```
   Render → Service → Environment
   Verify all keys are set correctly (no quotes, no spaces)
   ```

2. **Check Claude API quota:**
   ```
   Visit: console.anthropic.com
   Check if you have API credits remaining
   ```

3. **View Render logs:**
   ```
   Render → Service → Logs
   Look for Python errors or API failures
   ```

---

### Issue 3: Vercel Shows 404

**Symptoms:**
- "404: NOT_FOUND" error on Vercel

**Solutions:**

1. **Check Root Directory:**
   ```
   Vercel → Project → Settings → General
   Root Directory should be: frontend
   ```

2. **Check build logs:**
   ```
   Vercel → Deployments → Click deployment → View logs
   Look for build failures
   ```

3. **Redeploy:**
   ```
   Vercel → Deployments → Redeploy
   ```

---

### Issue 4: Slow First Load (30-60 seconds)

**Cause:** Render free tier "spins down" after 15 minutes of inactivity

**Solutions:**

1. **Expected behavior on free tier:**
   - First request: 30-60 seconds (cold start)
   - Subsequent requests: Fast

2. **Upgrade to paid tier ($7/month):**
   - Always-on (no cold starts)
   - Instant responses

3. **Or accept cold starts:**
   - Add loading message: "Backend warming up..."
   - Users will understand

---

## 💰 Cost Summary

### Free Tier (What You'll Use):

| Service | Cost | Limits |
|---------|------|--------|
| **Render Backend** | $0 | 750 hrs/month, spins down after 15 min |
| **Vercel Frontend** | $0 | 100 GB bandwidth/month |
| **Total** | **$0** | Great for demos/portfolios |

### Paid Tier (If Needed Later):

| Service | Cost | Benefits |
|---------|------|----------|
| **Render Backend** | $7/month | Always on, no cold starts |
| **Vercel Pro** | $20/month | More bandwidth, analytics |

**Recommendation:** Start with free tier!

---

## 🔄 Making Updates

### When You Update Code:

```bash
# 1. Make changes locally
# ... edit files ...

# 2. Test locally
cd backend
python app.py
# Test at localhost:5001

cd ../frontend
npm start
# Test at localhost:3000

# 3. Commit and push
git add .
git commit -m "Your update description"
git push origin data-nikhil

# 4. Auto-deployment happens!
# Both Render and Vercel watch your GitHub branch
# They auto-deploy when you push

# 5. Wait 2-5 minutes
# Check your live URLs to see updates
```

---

## 🎓 Understanding the Setup

### Why Two Deployments?

```
Vercel:
- Specializes in frontend (React, HTML, CSS, JS)
- Cannot run Python backend
- Perfect for static sites
- Super fast global CDN

Render:
- Supports backends (Python, Node, etc.)
- Can run Flask server
- Can make API calls to Claude, Google, etc.
- Persistent process needed for backend
```

### Why Not One Service?

**Can't use just Vercel:**
- Vercel doesn't support Python Flask apps
- Serverless functions have time limits (10s max)
- Your predictions take 3-6 seconds
- Need persistent Flask server

**Can't use just Render:**
- Render can host both, but:
- Static frontend is slower on Render
- Vercel's CDN is much faster for React apps
- Better to use each service for what it does best

---

## 📊 Performance Comparison

| Metric | Both Services | Just Render |
|--------|---------------|-------------|
| **Frontend Load** | 50-200ms (Vercel CDN) | 300-800ms |
| **Backend Response** | 3-6s (AI processing) | 3-6s |
| **Global Reach** | Excellent (Vercel edge) | Good |
| **Cold Start** | Frontend: No, Backend: Yes | Both: Yes |
| **Cost** | $0 | $0 |

**Conclusion:** Use both for best performance! ✅

---

## 🔐 Security Checklist

Before going live:

- [ ] `.env` not in Git (checked in .gitignore ✅)
- [ ] API keys in Render dashboard, not in code
- [ ] CORS configured properly (not `*` for production is better, but OK for demo)
- [ ] HTTPS enabled (automatic on both Render and Vercel ✅)
- [ ] No sensitive data in frontend code
- [ ] Backend validates all inputs
- [ ] Rate limiting considered (optional for demo)

---

## 📱 Share Your Live App

Once both are deployed, share:

```
🤖 My AI Prediction Tool is Live!

Frontend: https://poly-predictor.vercel.app
Backend: https://poly-predictor-backend.onrender.com/api/health

Features:
✓ Definitive YES/NO predictions
✓ Powered by Claude AI
✓ Real-time data from Google, NewsAPI, Yahoo Finance
✓ Hybrid confidence scoring
✓ Beautiful modern UI

Built with React, Tailwind, Flask, Claude AI

Try it now!
```

---

## ✅ TL;DR - Quick Summary

### What You Need:

1. **Backend on Render:**
   - Deploys Python Flask app
   - Handles AI predictions
   - URL: `https://your-backend.onrender.com`

2. **Frontend on Vercel:**
   - Deploys React UI
   - Calls backend API
   - URL: `https://your-frontend.vercel.app`

3. **Environment Variable on Vercel:**
   ```
   REACT_APP_API_URL = https://your-backend.onrender.com
   ```

### For Users to Access:

- They visit Vercel URL (frontend)
- Frontend automatically calls Render URL (backend)
- Everything works seamlessly!
- No setup needed for users ✅

---

## 🎉 Success!

When both are deployed:
- ✅ Anyone can visit your Vercel URL
- ✅ They can make predictions
- ✅ Backend processes requests
- ✅ Results appear instantly (after AI processing)
- ✅ Worldwide access
- ✅ No payment required

**Your app is now truly live and accessible to everyone!** 🚀

---

## 🆘 Need Help?

If you run into issues:

1. **Check Render logs** for backend errors
2. **Check Vercel logs** for build/deploy errors
3. **Check browser console** for frontend errors
4. **Verify environment variables** are set
5. **Test both URLs independently**

Both services have excellent documentation and support!

