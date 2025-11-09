# 🚀 Complete Application Running Guide

## Prerequisites Check

### ✅ Required Before Running:

```bash
# 1. Check if .env file exists with API key
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...

# 2. Check backend dependencies
cd backend
source venv/bin/activate
python -c "import flask, anthropic, sqlalchemy; print('✓ All packages installed')"

# 3. Check frontend dependencies
cd ../frontend
ls node_modules/ | wc -l
# Should show: ~1300 (packages installed)
```

---

## 🎯 Method 1: Run Full Application (Recommended)

### Terminal 1: Backend Server

```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon/backend
source venv/bin/activate
python app.py
```

**Expected Output:**
```
2025-11-08 16:37:02,731 INFO sqlalchemy.engine.Engine BEGIN (implicit)
✓ Database tables created successfully!
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Restarting with stat
 * Debugger is active!
```

### Terminal 2: Frontend Server

```bash
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon/frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

### Access the Application

1. **Browser opens automatically** at http://localhost:3000
2. **Enter a prediction query**
3. **Click "Get Prediction"**
4. **View results with confidence score**

---

## 🧪 Method 2: Test Backend Only

### Start Backend

```bash
cd backend
source venv/bin/activate
python app.py
```

### Test with cURL

```bash
# Terminal 3 (new terminal)

# Test 1: Health Check
curl http://localhost:5000/api/health
# Expected: {"status":"healthy"}

# Test 2: Make a Prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "Will Bitcoin reach $100k in 2025?"}'

# Test 3: Get History
curl http://localhost:5000/api/history?limit=5

# Test 4: Get Statistics
curl http://localhost:5000/api/stats
```

### Test with Python

```python
# test_api_manual.py
import requests
import json

BASE_URL = "http://localhost:5000"

# Test 1: Health Check
response = requests.get(f"{BASE_URL}/api/health")
print("Health:", response.json())

# Test 2: Make Prediction
response = requests.post(
    f"{BASE_URL}/api/predict",
    json={"query": "Will AI replace programmers?"}
)
result = response.json()
print(f"\nPrediction: {result['prediction'][:100]}...")
print(f"Confidence: {result['confidence_score']}%")

# Test 3: Get History
response = requests.get(f"{BASE_URL}/api/history?limit=5")
history = response.json()
print(f"\nTotal queries in history: {history['count']}")

# Test 4: Get Stats
response = requests.get(f"{BASE_URL}/api/stats")
stats = response.json()
print(f"\nDatabase Stats:")
print(f"  Total queries: {stats['total_queries']}")
print(f"  Average confidence: {stats['average_confidence_score']}%")
```

---

## 📊 Method 3: Test Database

```bash
cd backend
source venv/bin/activate
python test_database.py
```

**Expected Output:**
```
======================================================================
  🧪 DATABASE TEST SUITE
======================================================================

Test 1: Initializing database...
✓ Database initialized successfully!

Test 2: Saving sample prediction data...
✓ Sample data saved successfully!

[... more tests ...]

✓ ALL TESTS COMPLETED SUCCESSFULLY!
```

---

## 🎮 Method 4: Standalone Prediction Script

```bash
cd backend
source venv/bin/activate

# Interactive mode
python prediction_score.py

# OR with a specific query
python prediction_score.py "Trump 2024 election"
```

**This runs the Polymarket analysis script independently.**

---

## 🔍 Complete End-to-End Test

### Automated E2E Test Script

```bash
#!/bin/bash
# save as: test_e2e.sh

echo "🧪 Starting End-to-End Test..."
echo ""

# Check if backend is running
echo "1. Testing Backend Health..."
HEALTH=$(curl -s http://localhost:5000/api/health)
if [[ $HEALTH == *"healthy"* ]]; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend not running! Start with: python app.py"
    exit 1
fi

# Make a prediction
echo ""
echo "2. Making a prediction..."
PREDICTION=$(curl -s -X POST http://localhost:5000/api/predict \
    -H "Content-Type: application/json" \
    -d '{"query": "Will AI dominate by 2030?"}')

if [[ $PREDICTION == *"confidence_score"* ]]; then
    echo "   ✅ Prediction successful"
    CONFIDENCE=$(echo $PREDICTION | grep -o '"confidence_score":[0-9]*' | grep -o '[0-9]*')
    echo "   📊 Confidence Score: $CONFIDENCE%"
else
    echo "   ❌ Prediction failed"
    exit 1
fi

# Check database
echo ""
echo "3. Checking database..."
STATS=$(curl -s http://localhost:5000/api/stats)
TOTAL=$(echo $STATS | grep -o '"total_queries":[0-9]*' | grep -o '[0-9]*')
echo "   ✅ Total queries in database: $TOTAL"

# Check history
echo ""
echo "4. Checking history..."
HISTORY=$(curl -s http://localhost:5000/api/history?limit=3)
if [[ $HISTORY == *"queries"* ]]; then
    echo "   ✅ History retrieved successfully"
else
    echo "   ❌ History retrieval failed"
    exit 1
fi

# Check frontend
echo ""
echo "5. Testing Frontend..."
FRONTEND=$(curl -s http://localhost:3000)
if [[ $FRONTEND == *"html"* ]]; then
    echo "   ✅ Frontend is running"
else
    echo "   ⚠️  Frontend not running (optional)"
    echo "      Start with: npm start"
fi

echo ""
echo "======================================"
echo "✅ ALL TESTS PASSED!"
echo "======================================"
echo ""
echo "🚀 Your application is fully functional!"
echo ""
echo "Access points:"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:5000"
echo "  • Database:  backend/predictions.db"
```

**Run it:**
```bash
chmod +x test_e2e.sh
./test_e2e.sh
```

---

## 📋 Troubleshooting

### Backend Won't Start

```bash
# Check if .env file exists
cat .env

# Check if venv is activated
which python
# Should show: .../venv/bin/python

# Check for errors
python app.py
# Read error messages
```

### Frontend Won't Start

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install

# Try again
npm start
```

### Port Already in Use

```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# OR use a different port
# In app.py, change: app.run(debug=True, port=5001)
```

### API Key Error

```bash
# Make sure .env exists in ROOT directory
cd /Users/nikhil01/Desktop/Poly_Prediction_Tool/Claude-Hackathon
cat .env

# Should show:
# ANTHROPIC_API_KEY=sk-ant-...

# If missing, create it:
echo 'ANTHROPIC_API_KEY=your_key_here' > .env
```

---

## 📊 Verify Everything Works

### Complete Checklist:

```bash
# ✅ 1. Backend running?
curl http://localhost:5000/api/health

# ✅ 2. Frontend accessible?
curl http://localhost:3000

# ✅ 3. Can make predictions?
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"query": "Test query"}'

# ✅ 4. Database working?
curl http://localhost:5000/api/stats

# ✅ 5. History working?
curl http://localhost:5000/api/history

# ✅ 6. Database file exists?
ls -lh backend/predictions.db

# ✅ 7. Can query database?
sqlite3 backend/predictions.db "SELECT COUNT(*) FROM queries;"
```

---

## 🎯 Quick Commands Reference

### Start Everything:

```bash
# Terminal 1
cd backend && source venv/bin/activate && python app.py

# Terminal 2
cd frontend && npm start
```

### Stop Everything:

```bash
# In each terminal, press: Ctrl+C
```

### View Logs:

```bash
# Backend logs are in Terminal 1
# Frontend logs are in Terminal 2

# Database logs (if enabled in database.py)
# Shows all SQL queries
```

### Access Points:

```
Frontend (UI):        http://localhost:3000
Backend API:          http://localhost:5000
API Health:           http://localhost:5000/api/health
API History:          http://localhost:5000/api/history
API Stats:            http://localhost:5000/api/stats
Database File:        backend/predictions.db
```

---

## 🎉 Success Indicators

**Backend Running:**
```
✓ No errors in terminal
✓ Sees "Running on http://127.0.0.1:5000"
✓ Health endpoint responds
```

**Frontend Running:**
```
✓ Browser opens automatically
✓ Sees "Compiled successfully!"
✓ UI loads at localhost:3000
```

**Application Working:**
```
✓ Can enter queries in UI
✓ Predictions return with confidence scores
✓ Sources are displayed
✓ Data saved to database (check with /api/stats)
```

---

## 💡 Pro Tips

1. **Keep both terminals visible** - easier to see logs
2. **Check API endpoint first** before testing UI
3. **Use curl for quick tests** - faster than opening browser
4. **Check database stats** after each prediction to verify storage
5. **Use browser DevTools** (F12) to see network requests

---

## 🔗 Related Files

- `test_database.py` - Database testing
- `app.py` - Backend server
- `frontend/src/App.js` - Frontend UI
- `DATABASE_GUIDE.md` - Database documentation
- `QUICK_START.md` - Quick reference

---

## 🎊 You're All Set!

Your complete prediction tool with:
- ✅ Web scraping (DuckDuckGo)
- ✅ AI analysis (Claude)
- ✅ Database storage (SQLite)
- ✅ Beautiful UI (React)
- ✅ REST API
- ✅ Full documentation

**Just start both servers and go!** 🚀

