# 🚀 Quick Start Guide

## ⚡ TL;DR - Get Running in 3 Minutes

### 1. Create `.env` file (REQUIRED)
```bash
# In the root directory, create .env file:
echo 'ANTHROPIC_API_KEY=your_api_key_here' > .env
```
Replace `your_api_key_here` with your actual API key from https://console.anthropic.com/

### 2. Start Backend
```bash
cd backend
source venv/bin/activate  # Already set up!
python app.py
```
✅ Backend runs at: http://localhost:5000

### 3. Start Frontend (New Terminal)
```bash
cd frontend
npm start  # Dependencies already installed!
```
✅ Frontend runs at: http://localhost:3000

---

## 🎯 What You Can Do Now

### Option 1: Use the Web Interface
1. Open http://localhost:3000
2. Enter a prediction query
3. Get AI-powered analysis with confidence scores
4. **NEW:** Everything is automatically saved to database!

### Option 2: Use the Standalone Script
```bash
cd backend
python prediction_score.py
# Interactive mode - ask multiple questions

# OR with a specific query:
python prediction_score.py "Bitcoin $100k"
```

### Option 3: Use the API Directly
```bash
# Make a prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "Will AI replace programmers?"}'

# Get prediction history
curl http://localhost:5000/api/history?limit=10

# Get database stats
curl http://localhost:5000/api/stats
```

---

## 💾 Database Features (NEW!)

### What Gets Saved Automatically:
- ✅ Every query you make
- ✅ Every AI prediction
- ✅ All confidence scores
- ✅ Key factors and caveats
- ✅ Web sources used
- ✅ Timestamps

### Access Your Data:

**Via API:**
```bash
# Get recent predictions
curl http://localhost:5000/api/history

# Get specific query by ID
curl http://localhost:5000/api/query/1

# Get statistics
curl http://localhost:5000/api/stats
```

**Via SQLite:**
```bash
cd backend
sqlite3 predictions.db

# View your queries
SELECT * FROM queries LIMIT 5;

# View predictions with confidence
SELECT query_text, confidence_score 
FROM queries 
JOIN predictions ON queries.id = predictions.query_id;

# Exit
.quit
```

**Via Python:**
```python
from database import get_recent_queries, get_query_by_id

# Get last 10 predictions
history = get_recent_queries(limit=10)
print(history)

# Get specific prediction
query = get_query_by_id(1)
print(query)
```

---

## 📊 How Data Is Retrieved

### Current Implementation:

**1. Web Scraping (app.py):**
- Source: DuckDuckGo HTML search
- Returns: Title, snippet, URL
- Limit: Top 5 results

**2. AI Analysis (app.py):**
- Source: Claude API
- Input: Query + web sources
- Output: Prediction, confidence score, factors, caveats

**3. Polymarket Data (prediction_score.py):**
- Source: Polymarket Gamma API
- Returns: Market odds, volume, liquidity
- Use: Standalone script

**4. News Data (prediction_score.py):**
- Source: NewsAPI or mock data
- Returns: Articles with sentiment analysis
- Use: Standalone script

### Everything is saved to:
```
backend/predictions.db
├── queries (user questions)
├── predictions (AI responses)
├── sources (web data)
├── market_data (Polymarket)
└── news_articles (news data)
```

---

## 🔧 Test Your Setup

```bash
cd backend
source venv/bin/activate
python test_database.py
```

Should show:
```
✓ Database initialized successfully!
✓ Sample data saved successfully!
✓ Retrieved 2 recent queries
✓ Retrieved query ID 2
✓ Database statistics
...
✓ ALL TESTS COMPLETED SUCCESSFULLY!
```

---

## 📡 API Endpoints

### Core Endpoints:
- `POST /api/predict` - Make a prediction (saves to DB)
- `GET /api/history?limit=10` - Get recent predictions
- `GET /api/query/<id>` - Get specific query by ID
- `GET /api/stats` - Get database statistics
- `GET /api/health` - Health check

---

## 🗂️ Project Structure

```
Claude-Hackathon/
├── .env                          ← CREATE THIS (API key)
├── backend/
│   ├── app.py                    ← Main Flask server (modified)
│   ├── database.py               ← NEW! Database models
│   ├── test_database.py          ← NEW! Test script
│   ├── prediction_score.py       ← Standalone script
│   ├── predictions.db            ← NEW! Auto-created database
│   ├── requirements.txt          ← Updated with DB packages
│   └── venv/                     ← Already set up
├── frontend/
│   ├── src/
│   │   └── App.js                ← React frontend
│   └── node_modules/             ← Already installed
└── [Documentation]
    ├── README.md                 ← Original readme
    ├── DATA_FLOW_SUMMARY.md      ← NEW! Complete data flow guide
    ├── DATABASE_GUIDE.md         ← NEW! Detailed DB guide
    └── QUICK_START.md            ← This file
```

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check if .env file exists and has API key
cat .env

# Make sure venv is activated
source venv/bin/activate

# Check if all packages are installed
pip list | grep -E "flask|anthropic|sqlalchemy"
```

### Database issues?
```bash
# Reinitialize database
cd backend
python database.py

# Delete and recreate
rm predictions.db
python database.py
```

### Frontend issues?
```bash
# Reinstall packages
cd frontend
rm -rf node_modules
npm install
```

---

## 📚 Documentation Files

1. **QUICK_START.md** (this file) - Get started fast
2. **DATA_FLOW_SUMMARY.md** - Complete data flow explanation
3. **DATABASE_GUIDE.md** - Deep dive into database
4. **README.md** - Original project documentation

---

## ✨ What's New?

### Database Integration:
- ✅ Automatic storage of all predictions
- ✅ Query history tracking
- ✅ Source attribution
- ✅ Confidence score tracking
- ✅ Timestamp tracking
- ✅ New API endpoints for data retrieval
- ✅ SQLite database (easy, no setup)
- ✅ Test suite

### Updated Dependencies:
- ✅ SQLAlchemy 2.0.44 (database ORM)
- ✅ TextBlob 0.17.1 (sentiment analysis)

---

## 🎯 Common Use Cases

### 1. Make a prediction via web UI:
1. Open http://localhost:3000
2. Enter: "Will Tesla stock hit $500?"
3. View prediction + confidence score
4. Data automatically saved!

### 2. View prediction history:
```bash
curl http://localhost:5000/api/history
```

### 3. Analyze trends:
```bash
sqlite3 backend/predictions.db
SELECT DATE(created_at), AVG(confidence_score) 
FROM predictions 
GROUP BY DATE(created_at);
```

### 4. Export predictions:
```python
from database import get_recent_queries
import json

queries = get_recent_queries(limit=100)
with open('predictions_export.json', 'w') as f:
    json.dump(queries, f, indent=2)
```

---

## 💡 Pro Tips

1. **Check database stats regularly:**
   ```bash
   curl http://localhost:5000/api/stats
   ```

2. **Back up your database:**
   ```bash
   cp backend/predictions.db backend/predictions_backup.db
   ```

3. **View SQL queries:**
   - Check `database.py` - `echo=True` shows all SQL

4. **For production:**
   - Switch to PostgreSQL
   - Add user authentication
   - Deploy to cloud (Heroku, AWS, etc.)

---

## 🎉 You're Ready!

Your prediction tool now:
- ✅ Scrapes web data automatically
- ✅ Uses AI for analysis
- ✅ Saves everything to database
- ✅ Provides API access to historical data
- ✅ Has a beautiful frontend
- ✅ Is fully documented

**Start both servers and try it out!**

Questions? Check the documentation files or examine the code.

