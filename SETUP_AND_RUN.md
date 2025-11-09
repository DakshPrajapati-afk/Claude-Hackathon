# Poly Prediction Tool - Setup and Run Guide

## 📋 Prerequisites

Before you start, make sure you have:
- **Python 3.8+** installed
- **Node.js 14+** and npm installed
- **Git** installed
- API keys for:
  - Anthropic Claude API
  - Google Custom Search API
  - Google Custom Search Engine ID
  - NewsAPI
  - (Optional) Yahoo Finance and MarketWatch don't require keys

---

## 🚀 Initial Setup (First Time Only)

### Step 1: Clone the Repository

```bash
git clone https://github.com/DakshPrajapati-afk/Claude-Hackathon.git
cd Claude-Hackathon
```

### Step 2: Set Up Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Create `.env` File

Create a file called `.env` in the `backend` directory:

```bash
cd backend
nano .env  # Or use any text editor
```

Add your API keys:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NEWS_API_KEY=your_newsapi_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_custom_search_engine_id_here

# Optional (Reddit removed from this version)
# REDDIT_CLIENT_ID=your_reddit_client_id
# REDDIT_CLIENT_SECRET=your_reddit_client_secret
# REDDIT_USER_AGENT=your_app_name
```

**Important:** The `.env` file is in `.gitignore` and will NOT be committed to Git (it's secret!).

### Step 4: Set Up Frontend

```bash
# Navigate to frontend (from project root)
cd ../frontend

# Install Node.js dependencies
npm install
```

---

## ▶️ Running the Application

You need **TWO terminal windows** open:

### Terminal 1: Start Backend (Flask)

```bash
cd /path/to/Claude-Hackathon/backend
source venv/bin/activate
python app.py
```

You should see:
```
✓ Database tables created successfully!
 * Running on http://127.0.0.1:5001
```

### Terminal 2: Start Frontend (React)

```bash
cd /path/to/Claude-Hackathon/frontend
npm start
```

Your browser should automatically open to: **http://localhost:3000**

---

## 🛑 Stopping the Application

In each terminal window, press: **`Ctrl + C`**

---

## 🔄 Updating from Git (When You Pull New Changes)

```bash
# Pull latest changes
git pull origin data-nikhil

# Update backend dependencies (if requirements.txt changed)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies (if package.json changed)
cd ../frontend
npm install
```

Then restart both backend and frontend.

---

## 📤 Pushing Your Changes to GitHub

### Step 1: Check What Changed

```bash
cd /path/to/Claude-Hackathon
git status
```

### Step 2: Add Your Changes

```bash
# Add all changed files
git add .

# Or add specific files
git add backend/app.py
git add frontend/src/App.js
```

### Step 3: Commit Your Changes

```bash
git commit -m "Description of what you changed"
```

Example:
```bash
git commit -m "Added hybrid confidence scoring and removed Reddit API"
```

### Step 4: Push to GitHub

```bash
git push origin data-nikhil
```

If you get a "non-fast-forward" error:
```bash
# Pull first, then push
git pull origin data-nikhil
git push origin data-nikhil
```

---

## 🗂️ Project Structure

```
Claude-Hackathon/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── database.py               # Database models
│   ├── data_sources.py           # API integrations (Google, NewsAPI, Yahoo)
│   ├── source_quality.py         # Source scoring and filtering
│   ├── prediction_score.py       # Scoring logic
│   ├── requirements.txt          # Python dependencies
│   ├── venv/                     # Virtual environment (not in Git)
│   ├── .env                      # API keys (not in Git)
│   └── predictions.db            # SQLite database (not in Git)
├── frontend/
│   ├── src/
│   │   ├── App.js                # Main React component
│   │   ├── index.js              # React entry point
│   │   └── index.css             # Tailwind styles
│   ├── public/
│   │   └── index.html            # HTML template
│   ├── package.json              # Node dependencies
│   └── node_modules/             # NPM packages (not in Git)
├── .gitignore                    # Files to ignore in Git
├── README.md                     # Project overview
└── [Documentation files]         # Various .md guides
```

---

## 🔑 Getting API Keys

### 1. Anthropic Claude API
- Go to: https://console.anthropic.com/
- Sign up and create an API key
- Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### 2. NewsAPI
- Go to: https://newsapi.org/
- Sign up for free account
- Get API key from dashboard
- Add to `.env`: `NEWS_API_KEY=...`

### 3. Google Custom Search API
- Go to: https://console.cloud.google.com/
- Create a project
- Enable "Custom Search API"
- Create credentials (API key)
- Add to `.env`: `GOOGLE_API_KEY=...`

### 4. Google Custom Search Engine ID
- Go to: https://programmablesearchengine.google.com/
- Create a new search engine
- Set to search entire web
- Get the Search Engine ID
- Add to `.env`: `GOOGLE_CSE_ID=...`

---

## ⚠️ Common Issues and Fixes

### Issue: Port 5001 already in use
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Then restart backend
python app.py
```

### Issue: Port 3000 already in use
The frontend will ask if you want to use a different port. Type `Y` and press Enter.

### Issue: "Module not found" errors
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Issue: API errors (401, 403)
Check that your `.env` file has valid API keys with no extra spaces or quotes.

### Issue: "No data sources found"
- Verify API keys are correct
- Check internet connection
- Try a more specific query

### Issue: Git push rejected
```bash
# Pull first to sync with remote
git pull origin data-nikhil

# Resolve any conflicts if needed
# Then push
git push origin data-nikhil
```

---

## 📊 Features

### Active Data Sources (4 platforms):
1. ✅ **Google Custom Search** - General web search
2. ✅ **NewsAPI** - Credible news articles
3. ✅ **Yahoo Finance** - Market data (financial queries)
4. ✅ **MarketWatch** - Financial news (financial queries)

### Hybrid Confidence Scoring:
- **Objective Component (0-30 pts):** Scraped data quality (quantity, diversity, source reputation)
- **Subjective Component (0-40 pts):** Claude AI content analysis
- **Final Formula:** `40 + Data Quality + AI Analysis = Confidence %`

### Definitive Predictions:
- Every prediction starts with: YES, NO, HIGHLY LIKELY, or UNLIKELY
- No hedging or wavering
- Clear stance with supporting evidence

---

## 📚 Documentation Files

- **`SETUP_AND_RUN.md`** (this file) - How to set up and run
- **`LATEST_CHANGES.md`** - Recent updates summary
- **`REDDIT_REMOVED_AND_HYBRID_SCORING.md`** - Detailed explanation of hybrid scoring
- **`DATA_DRIVEN_CONFIDENCE.md`** - Complete confidence scoring guide
- **`DEFINITIVE_PREDICTIONS.md`** - How definitive predictions work
- **`CONFIDENCE_SCORING_GUIDE.md`** - User interpretation guide
- **`DATA_SOURCE_CHECKLIST.md`** - Data source verification

---

## 🧪 Testing the Application

### Test Query 1: Financial
```
"Will Apple stock reach $200 in 2025?"
```
Expected: Uses 3-4 platforms (Google, NewsAPI, Yahoo Finance, MarketWatch)

### Test Query 2: Technology
```
"Will GPT-5 be released in 2025?"
```
Expected: Uses 2-3 platforms (Google, NewsAPI)

### Test Query 3: General
```
"Will Bitcoin reach $100k in 2025?"
```
Expected: Uses all 4 platforms, high confidence if sources agree

---

## 🔒 Security Notes

**Never commit these files:**
- ❌ `.env` (contains API keys)
- ❌ `venv/` (virtual environment)
- ❌ `node_modules/` (NPM packages)
- ❌ `predictions.db` (local database)
- ❌ `__pycache__/` (Python cache)

These are already in `.gitignore`, but be careful not to force-add them.

---

## 🤝 Contributing

If you're working with a team:

1. **Pull before you start working:**
   ```bash
   git pull origin data-nikhil
   ```

2. **Work on your changes**

3. **Commit with clear messages:**
   ```bash
   git commit -m "Clear description of what changed"
   ```

4. **Push frequently:**
   ```bash
   git push origin data-nikhil
   ```

5. **Communicate with team** about major changes

---

## 🆘 Getting Help

If something doesn't work:

1. Check this guide first
2. Look at the relevant documentation files
3. Check terminal error messages
4. Verify API keys in `.env`
5. Try restarting both backend and frontend

---

## ✅ Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 14+ installed
- [ ] Repository cloned
- [ ] Backend virtual environment created
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running on port 5001
- [ ] Frontend running on port 3000
- [ ] Browser opened to http://localhost:3000

**Ready to make predictions!** 🎯

