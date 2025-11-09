# 📊 Database Storage Guide

## Overview

Your prediction tool now automatically saves all data to a database! This allows you to:
- Store prediction history
- Track confidence scores over time
- Keep web sources for reference
- Analyze trends in predictions

## 🗄️ Database Schema

### Tables

#### 1. **queries**
Stores user queries
- `id`: Primary key
- `query_text`: The user's question
- `created_at`: When the query was made

#### 2. **predictions**
Stores AI-generated predictions
- `id`: Primary key
- `query_id`: Foreign key to queries
- `prediction_text`: The prediction
- `confidence_score`: 0-100 score
- `key_factors`: JSON array of factors
- `caveats`: JSON array of caveats
- `model_used`: AI model name
- `created_at`: When prediction was made

#### 3. **sources**
Stores web sources used for predictions
- `id`: Primary key
- `query_id`: Foreign key to queries
- `title`: Source title
- `snippet`: Source excerpt
- `url`: Source URL
- `source_name`: Publisher name
- `retrieved_at`: When source was scraped

#### 4. **market_data**
Stores Polymarket prediction market data
- `id`: Primary key
- `query_id`: Foreign key to queries (nullable)
- `question`: Market question
- `slug`: URL identifier
- `yes_price`, `no_price`: Odds (0.0-1.0)
- `volume`, `liquidity`: Trading metrics
- `end_date`: Market close date

#### 5. **news_articles**
Stores news articles for analysis
- `id`: Primary key
- `query_id`: Foreign key to queries (nullable)
- `title`: Article headline
- `source`: Publication name
- `date`: Publication date
- `summary`: Article summary
- `sentiment`: positive/negative/neutral

## 🔄 Data Flow

### Current Flow (with Database):

```
User Query
    ↓
[1] Web Scraping (DuckDuckGo)
    ↓
[2] Claude AI Analysis
    ↓
[3] Save to Database ✅ NEW!
    ↓
[4] Return to Frontend
```

### What Gets Saved:

Every time a user makes a prediction query:
1. ✅ Query text is saved
2. ✅ AI prediction is saved
3. ✅ Confidence score is saved
4. ✅ Key factors are saved
5. ✅ Caveats are saved
6. ✅ All web sources are saved
7. ✅ Timestamps are recorded

## 🚀 How to Use

### Initialize Database

First time setup:
```bash
cd backend
source venv/bin/activate
python database.py
```

This creates `predictions.db` in your backend folder.

### Run the Application

```bash
python app.py
```

The database will automatically initialize on startup!

## 📡 New API Endpoints

### 1. Get Prediction History
```bash
GET /api/history?limit=10
```

**Response:**
```json
{
  "count": 10,
  "queries": [
    {
      "id": 1,
      "query_text": "Will electric vehicles dominate by 2030?",
      "created_at": "2025-11-08T10:30:00",
      "predictions": [
        {
          "prediction_text": "Yes, likely...",
          "confidence_score": 75,
          "key_factors": ["..."],
          "caveats": ["..."]
        }
      ]
    }
  ]
}
```

### 2. Get Specific Query
```bash
GET /api/query/1
```

**Response:**
```json
{
  "id": 1,
  "query_text": "Will electric vehicles dominate by 2030?",
  "created_at": "2025-11-08T10:30:00",
  "predictions": [...],
  "sources": [
    {
      "id": 1,
      "title": "Source title",
      "snippet": "Source content",
      "url": "https://..."
    }
  ]
}
```

### 3. Get Statistics
```bash
GET /api/stats
```

**Response:**
```json
{
  "total_queries": 42,
  "total_predictions": 42,
  "total_sources": 210,
  "average_confidence_score": 67.5
}
```

## 🔍 Querying the Database Directly

### Using Python:

```python
from database import SessionLocal, Query, Prediction

# Get database session
db = SessionLocal()

# Get all queries
queries = db.query(Query).all()

# Get predictions with high confidence
high_confidence = db.query(Prediction).filter(
    Prediction.confidence_score >= 80
).all()

# Get recent queries
from sqlalchemy import desc
recent = db.query(Query).order_by(
    desc(Query.created_at)
).limit(5).all()

db.close()
```

### Using SQLite CLI:

```bash
# Open database
sqlite3 predictions.db

# View tables
.tables

# Query data
SELECT * FROM queries LIMIT 5;
SELECT AVG(confidence_score) FROM predictions;
SELECT query_text, confidence_score FROM queries 
JOIN predictions ON queries.id = predictions.query_id
ORDER BY predictions.created_at DESC LIMIT 10;

# Exit
.quit
```

## 🔧 Database Configuration

### SQLite (Default - Development)
```python
# In database.py
DATABASE_URL = 'sqlite:///predictions.db'
```
- ✅ No setup required
- ✅ Easy to use
- ⚠️ Single file database
- ⚠️ Not suitable for high concurrency

### PostgreSQL (Production)
```python
# In database.py or .env
DATABASE_URL = 'postgresql://username:password@localhost/prediction_db'
```
- ✅ Production-ready
- ✅ Better performance
- ✅ Supports multiple connections
- ⚠️ Requires PostgreSQL installation

To switch to PostgreSQL:
1. Install PostgreSQL
2. Create database: `createdb prediction_db`
3. Add to `.env`: `DATABASE_URL=postgresql://...`
4. Install psycopg2: `pip install psycopg2-binary`

## 📊 Analyzing Your Data

### Export to CSV:

```python
import pandas as pd
from database import SessionLocal, Query, Prediction

db = SessionLocal()

# Get all predictions with queries
results = db.query(
    Query.query_text,
    Prediction.confidence_score,
    Prediction.prediction_text,
    Prediction.created_at
).join(Prediction).all()

df = pd.DataFrame(results, columns=[
    'query', 'confidence', 'prediction', 'date'
])

df.to_csv('predictions_export.csv', index=False)
db.close()
```

### Analyze Trends:

```python
from database import SessionLocal, Prediction
from sqlalchemy import func

db = SessionLocal()

# Average confidence by date
avg_by_date = db.query(
    func.date(Prediction.created_at),
    func.avg(Prediction.confidence_score)
).group_by(func.date(Prediction.created_at)).all()

print("Average confidence scores over time:")
for date, avg_score in avg_by_date:
    print(f"{date}: {avg_score:.1f}%")

db.close()
```

## 🧹 Database Maintenance

### View Database Size:
```bash
ls -lh predictions.db
```

### Backup Database:
```bash
cp predictions.db predictions_backup_$(date +%Y%m%d).db
```

### Clear Old Data:
```python
from database import SessionLocal, Query
from datetime import datetime, timedelta

db = SessionLocal()

# Delete queries older than 30 days
cutoff_date = datetime.utcnow() - timedelta(days=30)
db.query(Query).filter(Query.created_at < cutoff_date).delete()
db.commit()
db.close()
```

## 🐛 Troubleshooting

### "Database is locked" error:
- Close all connections to the database
- Make sure only one process is writing at a time
- Consider switching to PostgreSQL for production

### "Table doesn't exist" error:
```bash
python database.py
```
This will recreate all tables.

### View database logs:
Check `database.py` - SQLAlchemy has `echo=True` which prints all SQL queries.

## 🎯 Next Steps

1. ✅ Database is now automatically saving all predictions
2. Consider adding user authentication to track individual users
3. Add data visualization dashboard
4. Implement search functionality
5. Export predictions to PDF/Excel
6. Add email notifications for predictions

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

