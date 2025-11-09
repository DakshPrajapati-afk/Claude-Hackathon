# Deployment Guide - Make Your App Accessible Online

## 🌐 Overview

To make your Poly Prediction Tool accessible to others, you need to deploy both:
1. **Backend (Flask API)** - Needs to run on a server
2. **Frontend (React UI)** - Needs to be hosted and configured to call the backend

---

## 🎯 Recommended Deployment Options

### Option 1: Render (Easiest - FREE Tier Available) ⭐ RECOMMENDED

**Best for:** Quick deployment, free hosting, automatic deployments

**Pros:**
- ✅ Free tier available
- ✅ Very easy setup
- ✅ Automatic deployments from GitHub
- ✅ HTTPS included
- ✅ Handles both backend and frontend

**Cons:**
- ⚠️ Free tier spins down after inactivity (cold starts)
- ⚠️ Limited resources on free tier

### Option 2: Vercel (Frontend) + Render (Backend)

**Best for:** Best performance for React apps, free tier

**Pros:**
- ✅ Excellent React/Next.js support
- ✅ Very fast CDN
- ✅ Free tier generous
- ✅ Easy GitHub integration

### Option 3: Heroku

**Best for:** Traditional deployment, more control

**Pros:**
- ✅ Well-documented
- ✅ Add-ons ecosystem
- ✅ Good for Flask apps

**Cons:**
- ⚠️ No longer has free tier (starts at $7/month)

### Option 4: AWS/DigitalOcean/Google Cloud

**Best for:** Production apps, scalability, full control

**Pros:**
- ✅ Full control
- ✅ Scalable
- ✅ Professional

**Cons:**
- ❌ More complex
- ❌ Costs money
- ❌ Requires DevOps knowledge

---

## 🚀 QUICKEST DEPLOYMENT: Render (Step-by-Step)

### Prerequisites
- ✅ GitHub account with your code pushed
- ✅ Render account (free at https://render.com)
- ✅ API keys ready

---

## Part 1: Deploy Backend (Flask API) on Render

### Step 1: Prepare Backend for Deployment

First, create necessary configuration files:

#### 1.1 Create `render.yaml` in project root

```bash
cd /path/to/Claude-Hackathon
nano render.yaml
```

Add this content:

```yaml
services:
  - type: web
    name: poly-predictor-backend
    env: python
    region: oregon
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && gunicorn app:app"
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: NEWS_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: GOOGLE_CSE_ID
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

#### 1.2 Add Gunicorn to requirements.txt

```bash
cd backend
nano requirements.txt
```

Add this line at the end:
```
gunicorn==21.2.0
```

#### 1.3 Update `app.py` for production

At the very end of `backend/app.py`, change:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

To:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
```

And add this import at the top:
```python
import os
```

#### 1.4 Commit and push changes

```bash
cd /path/to/Claude-Hackathon
git add .
git commit -m "Added deployment configuration for Render"
git push origin data-nikhil
```

### Step 2: Deploy on Render

1. Go to https://render.com and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your repository: `Claude-Hackathon`
5. Configure:
   - **Name:** `poly-predictor-backend`
   - **Region:** Oregon (or closest to you)
   - **Branch:** `data-nikhil`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Click **"Advanced"** and add environment variables:
   - `ANTHROPIC_API_KEY` = your_key
   - `NEWS_API_KEY` = your_key
   - `GOOGLE_API_KEY` = your_key
   - `GOOGLE_CSE_ID` = your_cse_id
7. Click **"Create Web Service"**

Wait 5-10 minutes for deployment. You'll get a URL like:
```
https://poly-predictor-backend.onrender.com
```

### Step 3: Test Backend

Visit:
```
https://poly-predictor-backend.onrender.com/api/health
```

Should return:
```json
{"status": "healthy"}
```

---

## Part 2: Deploy Frontend (React) on Render

### Step 1: Prepare Frontend

#### 1.1 Update API URL in frontend

Create `frontend/.env.production`:

```bash
cd frontend
nano .env.production
```

Add:
```
REACT_APP_API_URL=https://poly-predictor-backend.onrender.com
```

#### 1.2 Update `frontend/src/App.js`

Change the API URL to use environment variable:

Find this line (around line 18):
```javascript
const response = await axios.post('http://localhost:5001/api/predict', {
```

Replace with:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
const response = await axios.post(`${API_URL}/api/predict`, {
```

#### 1.3 Create `frontend/package.json` build script

Make sure your `package.json` has:
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

#### 1.4 Commit changes

```bash
cd /path/to/Claude-Hackathon
git add .
git commit -m "Configured frontend for production deployment"
git push origin data-nikhil
```

### Step 2: Deploy Frontend on Render

1. Go to Render dashboard
2. Click **"New +"** → **"Static Site"**
3. Select your repository: `Claude-Hackathon`
4. Configure:
   - **Name:** `poly-predictor-frontend`
   - **Branch:** `data-nikhil`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
5. Add environment variable:
   - `REACT_APP_API_URL` = `https://poly-predictor-backend.onrender.com`
6. Click **"Create Static Site"**

Wait 5-10 minutes. You'll get a URL like:
```
https://poly-predictor-frontend.onrender.com
```

### Step 3: Update Backend CORS

Update `backend/app.py` to allow your frontend domain:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://poly-predictor-frontend.onrender.com"  # Add your frontend URL
        ]
    }
})
```

Commit and push:
```bash
git add backend/app.py
git commit -m "Updated CORS for production frontend"
git push origin data-nikhil
```

Render will automatically redeploy the backend.

---

## ✅ Your App is Now Live!

Visit: **https://poly-predictor-frontend.onrender.com**

Share this URL with anyone! 🎉

---

## 🔧 Alternative: Vercel (Frontend Only)

If you want even better frontend performance:

### Deploy Frontend on Vercel

1. Go to https://vercel.com and sign up
2. Click **"Import Project"**
3. Connect GitHub and select `Claude-Hackathon`
4. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
5. Add environment variable:
   - `REACT_APP_API_URL` = `https://poly-predictor-backend.onrender.com`
6. Deploy

You'll get a URL like: `https://poly-predictor.vercel.app`

Update backend CORS to include this new URL.

---

## 💰 Cost Comparison

| Service | Backend | Frontend | Total/Month |
|---------|---------|----------|-------------|
| **Render (Free)** | Free | Free | $0 |
| **Render (Paid)** | $7 | Free | $7 |
| **Vercel + Render** | Free | Free | $0 |
| **Heroku** | $7 | $7 | $14 |
| **AWS/DigitalOcean** | ~$10 | ~$5 | ~$15 |

**Recommendation:** Start with Render free tier. Upgrade if you need better performance.

---

## ⚠️ Important Considerations

### 1. API Keys Security

**NEVER commit `.env` to Git** (already in .gitignore ✅)

Add API keys through:
- Render dashboard → Environment Variables
- Vercel dashboard → Environment Variables

### 2. Database

Your SQLite database (`predictions.db`) is ephemeral on free tiers. For persistent storage:

**Option A:** Upgrade to paid tier with persistent storage
**Option B:** Use a managed database (PostgreSQL):
- Render PostgreSQL (free tier available)
- Supabase (free tier)
- Railway (free tier)

### 3. Cold Starts

Free tiers "spin down" after 15 minutes of inactivity:
- First request takes 30-60 seconds
- Subsequent requests are fast
- Upgrade to paid tier for always-on

### 4. Rate Limits

Monitor your API usage:
- Anthropic Claude API
- NewsAPI (free tier: 100 requests/day)
- Google Custom Search (100 queries/day free)

---

## 🚀 Custom Domain (Optional)

### Buy a Domain
- Namecheap (~$10/year)
- Google Domains (~$12/year)
- GoDaddy (~$15/year)

### Configure on Render
1. Go to your service → Settings → Custom Domain
2. Add your domain: `polypredictions.com`
3. Update DNS records as shown
4. Wait for SSL certificate (automatic)

### Configure on Vercel
1. Project → Settings → Domains
2. Add domain
3. Update DNS records
4. Done!

---

## 📊 Monitoring and Maintenance

### Monitor Your Deployment

**Render:**
- Dashboard shows logs in real-time
- Metrics tab shows CPU/memory usage
- Alerts for downtime

**Vercel:**
- Analytics built-in
- Performance insights
- Error tracking

### Keep Your App Updated

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push origin data-nikhil

# Render/Vercel auto-deploys from GitHub!
```

---

## 🐛 Common Deployment Issues

### Issue 1: "Application Error" on Backend
**Solution:** Check logs in Render dashboard
- Look for missing dependencies
- Check environment variables are set
- Verify API keys are correct

### Issue 2: Frontend Can't Connect to Backend
**Solution:** Check CORS configuration
- Backend CORS must include frontend URL
- Frontend `.env.production` must have correct API URL

### Issue 3: "Build Failed"
**Solution:** Check build logs
- Ensure `requirements.txt` / `package.json` are correct
- Check for typos in build commands
- Verify Python/Node versions

### Issue 4: API Keys Not Working
**Solution:** 
- Copy keys directly without extra spaces
- Don't include quotes in environment variables
- Restart service after adding variables

### Issue 5: Database Data Lost
**Solution:** Free tier storage is ephemeral
- Upgrade to paid tier with persistent disk
- Or migrate to PostgreSQL

---

## 📚 Step-by-Step Checklist

### Backend Deployment ✅
- [ ] Add `gunicorn` to `requirements.txt`
- [ ] Update `app.py` to use PORT environment variable
- [ ] Create Render account
- [ ] Create Web Service on Render
- [ ] Add environment variables (API keys)
- [ ] Wait for deployment
- [ ] Test `/api/health` endpoint

### Frontend Deployment ✅
- [ ] Create `.env.production` with backend URL
- [ ] Update `App.js` to use environment variable
- [ ] Commit and push changes
- [ ] Create Static Site on Render (or Vercel)
- [ ] Add `REACT_APP_API_URL` environment variable
- [ ] Wait for deployment
- [ ] Test the website

### Post-Deployment ✅
- [ ] Update backend CORS with frontend URL
- [ ] Test predictions end-to-end
- [ ] Share URL with others
- [ ] Monitor logs and usage
- [ ] Set up custom domain (optional)

---

## 🎓 Learning Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [React Deployment](https://create-react-app.dev/docs/deployment/)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check logs** in Render/Vercel dashboard
2. **Test locally** first (`npm start` and `python app.py`)
3. **Verify environment variables** are set correctly
4. **Check CORS** configuration
5. **Review deployment logs** for error messages

---

## 🌟 Summary

**Easiest Path:**
1. Deploy backend on Render (free tier)
2. Deploy frontend on Render (free tier)
3. Update CORS configuration
4. Share your URL!

**Total time:** ~30-60 minutes  
**Total cost:** $0 (free tier)

Your Poly Prediction Tool will be live at:
```
https://poly-predictor-frontend.onrender.com
```

**Anyone with the link can use it!** 🎉

---

## 🔐 Security Checklist

Before going live:
- [ ] `.env` is in `.gitignore` (already done ✅)
- [ ] API keys are set via dashboard, not in code
- [ ] CORS is configured (not `*`)
- [ ] Debug mode is OFF in production
- [ ] HTTPS is enabled (automatic on Render/Vercel)
- [ ] Rate limiting considered for API endpoints
- [ ] Database backups configured (if using paid tier)

---

**Ready to deploy? Follow the Render guide above and your app will be live in under an hour!** 🚀

