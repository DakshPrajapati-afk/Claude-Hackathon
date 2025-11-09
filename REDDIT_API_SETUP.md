# 🔴 Reddit API Setup Guide

## Why Reddit?
- ✅ Community sentiment and discussions
- ✅ Real-time opinions on prediction markets
- ✅ Subreddits like r/wallstreetbets, r/politics, r/cryptocurrency
- ✅ Completely FREE with generous rate limits

---

## 📋 Step-by-Step Setup (5 minutes)

### Step 1: Create a Reddit Account
If you don't have one: https://www.reddit.com/register/

### Step 2: Create a Reddit App

1. **Go to:** https://www.reddit.com/prefs/apps
   
2. **Scroll to bottom** and click "**create another app...**" (or "create app")

3. **Fill in the form:**
   ```
   Name: Polymarket Predictor
   App type: ○ script
   Description: Prediction market analysis tool
   About URL: (leave blank)
   Redirect URI: http://localhost:8080
   ```

4. **Click "create app"**

### Step 3: Get Your Credentials

After creating, you'll see:

```
┌─────────────────────────────────────────┐
│ Polymarket Predictor                    │
│ personal use script                      │
│                                         │
│ [14 character string]  ← client_id      │
│                                         │
│ secret: [secret key]   ← client_secret  │
│                                         │
│ http://localhost:8080                   │
└─────────────────────────────────────────┘
```

**Copy these 2 values:**
- **client_id**: The 14-character string under your app name
- **client_secret**: The string after "secret:"

---

## 🔧 Add to Your `.env` File

Open: `/Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon/.env`

Add these lines:

```bash
# Reddit API
REDDIT_CLIENT_ID=your_14_character_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=PolymarketPredictor/1.0
```

**Example:**
```bash
REDDIT_CLIENT_ID=abcd1234efgh56
REDDIT_CLIENT_SECRET=xyz789_abcdef123456
REDDIT_USER_AGENT=PolymarketPredictor/1.0
```

---

## 📊 Rate Limits

**Free Tier:**
- 60 requests per minute
- No daily limit
- More than enough for your use case!

---

## 🎯 What You'll Get

Reddit will search for discussions in relevant subreddits:

**For election queries:**
- r/politics
- r/PoliticalDiscussion
- r/Conservative
- r/Liberal

**For crypto/finance queries:**
- r/cryptocurrency
- r/Bitcoin
- r/wallstreetbets
- r/investing

**For general predictions:**
- r/Polymarket
- r/PredictionMarkets
- Search across all of Reddit

---

## 🔗 Useful Links

- **Create App:** https://www.reddit.com/prefs/apps
- **API Documentation:** https://www.reddit.com/dev/api/
- **PRAW Documentation:** https://praw.readthedocs.io/en/stable/
- **Reddit Rules:** https://www.redditinc.com/policies/data-api-terms

---

## ✅ Quick Check

After adding to `.env`:

```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon
cat .env | grep REDDIT
```

Should show your Reddit credentials.

---

## 🆘 Troubleshooting

### "invalid_grant" error
- Make sure you selected "**script**" as app type, not "web app"

### "403 Forbidden" error
- Check your `REDDIT_USER_AGENT` is set correctly
- Format: `YourAppName/1.0` (no spaces)

### Can't find the app
- Go to https://www.reddit.com/prefs/apps
- Scroll to the very bottom of the page

---

## 🎉 Next Steps

After adding keys to `.env`:
1. Install dependencies (done automatically)
2. Restart backend
3. Reddit will be included in search results!

