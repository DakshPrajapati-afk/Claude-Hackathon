# Quick Deployment Checklist

## ⚡ Deploy Your App in 30 Minutes

Follow this checklist to deploy your Poly Prediction Tool to the web!

---

## ✅ Pre-Deployment Checklist

### 1. Verify Local Setup Works
- [ ] Backend runs: `cd backend && source venv/bin/activate && python app.py`
- [ ] Frontend runs: `cd frontend && npm start`
- [ ] Can make predictions successfully
- [ ] Have all API keys ready

### 2. Prepare Code for Deployment
- [ ] All changes committed to Git
- [ ] Pushed to GitHub branch `data-nikhil`
- [ ] `.env` file is NOT in Git (check `.gitignore`)
- [ ] `gunicorn` added to `requirements.txt` ✅ (already done)
- [ ] `render.yaml` exists in project root ✅ (already done)

---

## 🚀 Deployment Steps

### Step 1: Sign Up for Render (2 minutes)

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render to access your repositories

### Step 2: Deploy Backend (10 minutes)

1. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select `Claude-Hackathon` repository
   - Name: `poly-predictor-backend`
   - Branch: `data-nikhil`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

2. **Add Environment Variables** (Click "Advanced")
   ```
   ANTHROPIC_API_KEY = [your key]
   NEWS_API_KEY = [your key]
   GOOGLE_API_KEY = [your key]
   GOOGLE_CSE_ID = [your key]
   FLASK_ENV = production
   ```

3. **Click "Create Web Service"**
   - Wait 5-10 minutes for deployment
   - Note your backend URL: `https://poly-predictor-backend.onrender.com`

4. **Test Backend**
   - Visit: `https://poly-predictor-backend.onrender.com/api/health`
   - Should see: `{"status": "healthy"}`

### Step 3: Deploy Frontend (10 minutes)

1. **Create `.env.production` locally**
   ```bash
   cd frontend
   echo "REACT_APP_API_URL=https://poly-predictor-backend.onrender.com" > .env.production
   ```

2. **Update `App.js`** (find around line 18)
   
   Change from:
   ```javascript
   const response = await axios.post('http://localhost:5001/api/predict', {
   ```
   
   To:
   ```javascript
   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
   const response = await axios.post(`${API_URL}/api/predict`, {
   ```

3. **Commit Changes**
   ```bash
   cd /path/to/Claude-Hackathon
   git add .
   git commit -m "Configured frontend for production"
   git push origin data-nikhil
   ```

4. **Create Static Site on Render**
   - Click "New +" → "Static Site"
   - Select `Claude-Hackathon` repository
   - Name: `poly-predictor-frontend`
   - Branch: `data-nikhil`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `build`

5. **Add Environment Variable**
   ```
   REACT_APP_API_URL = https://poly-predictor-backend.onrender.com
   ```

6. **Click "Create Static Site"**
   - Wait 5-10 minutes
   - Note your frontend URL: `https://poly-predictor-frontend.onrender.com`

### Step 4: Update Backend CORS (5 minutes)

1. **Edit `backend/app.py`**
   
   Find the CORS configuration and update:
   ```python
   CORS(app, resources={
       r"/api/*": {
           "origins": [
               "http://localhost:3000",
               "https://poly-predictor-frontend.onrender.com"  # Your frontend URL
           ]
       }
   })
   ```

2. **Commit and Push**
   ```bash
   git add backend/app.py
   git commit -m "Updated CORS for production"
   git push origin data-nikhil
   ```

3. **Wait for Auto-Redeploy**
   - Render detects the push and redeploys automatically
   - Wait 2-3 minutes

### Step 5: Test Your Live App (2 minutes)

1. Visit your frontend URL: `https://poly-predictor-frontend.onrender.com`
2. Try a prediction: "Will Bitcoin reach $100k in 2025?"
3. Verify you see results with confidence score

---

## 🎉 Success!

Your app is now LIVE and accessible to anyone!

**Share your URL:**
```
https://poly-predictor-frontend.onrender.com
```

---

## 📱 Share Your App

Send this link to anyone:
- Friends
- Family
- Social media
- Hackathon judges

They can access it immediately - no setup required!

---

## 🔧 Making Updates

When you want to update your deployed app:

```bash
# 1. Make your changes locally
# ... edit files ...

# 2. Commit and push
git add .
git commit -m "Description of changes"
git push origin data-nikhil

# 3. Render auto-deploys in 2-5 minutes!
```

No need to redeploy manually - Render watches your GitHub branch!

---

## ⚠️ Common Issues

### Issue: Backend shows "Application Error"
**Fix:**
1. Go to Render dashboard → Your backend service
2. Click "Logs" tab
3. Look for error messages
4. Usually: missing environment variables

### Issue: Frontend can't reach backend
**Fix:**
1. Check CORS in `backend/app.py` includes your frontend URL
2. Check `.env.production` has correct backend URL
3. Redeploy both services

### Issue: "Build Failed"
**Fix:**
1. Check build logs in Render dashboard
2. Verify `requirements.txt` / `package.json` are correct
3. Check Python/Node versions

### Issue: Slow first load
**Normal:** Free tier spins down after 15 minutes of inactivity
- First request takes 30-60 seconds
- Subsequent requests are fast
- Upgrade to paid tier ($7/month) for always-on

---

## 💰 Cost

**Free Tier:**
- ✅ Backend: Free
- ✅ Frontend: Free
- ⚠️ Spins down after 15 min inactivity
- ⚠️ 750 hours/month limit

**Paid Tier ($7/month):**
- ✅ Always on (no spin down)
- ✅ Faster performance
- ✅ More resources
- ✅ Persistent storage

**Start with free tier** - upgrade if you need better performance!

---

## 🎓 Next Steps

### Optional Improvements:

1. **Custom Domain** ($10-15/year)
   - Buy: polypredictions.com
   - Configure in Render settings
   - Professional look!

2. **PostgreSQL Database** (Free tier available)
   - Replace SQLite for persistent data
   - Add Render PostgreSQL service
   - Update connection string

3. **Monitoring**
   - Set up health check alerts
   - Monitor API usage
   - Track response times

4. **Analytics**
   - Add Google Analytics
   - Track user behavior
   - See popular queries

---

## 📊 Deployment URLs

After deployment, update this section:

**Backend API:**
```
https://poly-predictor-backend.onrender.com
```

**Frontend App:**
```
https://poly-predictor-frontend.onrender.com
```

**API Health Check:**
```
https://poly-predictor-backend.onrender.com/api/health
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend is live and responding to `/api/health`
- [ ] Frontend loads successfully
- [ ] Can make a test prediction
- [ ] CORS configured correctly
- [ ] All API keys working
- [ ] Shared URL with others
- [ ] Monitoring deployment logs

---

## 🆘 Need Help?

If you get stuck:

1. **Check Render Logs**
   - Dashboard → Service → Logs tab
   - Look for error messages

2. **Test Locally First**
   - Does it work on localhost?
   - If yes, it's a deployment config issue
   - If no, fix the code first

3. **Review Environment Variables**
   - Backend: API keys set correctly?
   - Frontend: Backend URL correct?

4. **CORS Issues**
   - Backend must allow frontend origin
   - No wildcards (`*`) in production

---

## 🎯 Summary

**Total Time:** ~30 minutes  
**Total Cost:** $0 (free tier)  
**Result:** Live app accessible to anyone worldwide! 🌍

**Your deployment is complete when:**
- ✅ You can visit your frontend URL
- ✅ You can make a prediction
- ✅ You see results with confidence score
- ✅ Others can access it via the link

**Congratulations!** 🎉 Your app is now on the internet!

