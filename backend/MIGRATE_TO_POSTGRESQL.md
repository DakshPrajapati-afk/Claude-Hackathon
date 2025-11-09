# 🚀 Migrating from SQLite to PostgreSQL

## Overview

This guide shows you how to migrate from the current SQLite setup to a PostgreSQL server-based database.

---

## 🎯 Why Migrate?

### Current (SQLite):
- ✅ Simple, no setup
- ✅ Perfect for development
- ❌ Single writer at a time
- ❌ Not ideal for production

### PostgreSQL:
- ✅ Multiple concurrent users
- ✅ Production-ready
- ✅ Better performance at scale
- ✅ Advanced features
- ⚠️ Requires server setup

---

## 📋 Step-by-Step Migration

### Step 1: Install PostgreSQL

#### On macOS:
```bash
# Using Homebrew
brew install postgresql@15

# Start PostgreSQL server
brew services start postgresql@15

# Verify it's running
pg_isready
# Output: /tmp:5432 - accepting connections
```

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

#### On Windows:
1. Download installer from: https://www.postgresql.org/download/windows/
2. Run installer (choose default port 5432)
3. Remember the password you set!

---

### Step 2: Create Database

```bash
# Open PostgreSQL prompt
psql postgres

# Inside psql:
CREATE DATABASE prediction_db;

# Create user (optional, recommended)
CREATE USER prediction_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE prediction_db TO prediction_user;

# Exit
\q
```

**OR use default postgres user:**
```bash
# Just create the database
createdb prediction_db
```

---

### Step 3: Install Python Driver

```bash
cd backend
source venv/bin/activate

# Install PostgreSQL driver
pip install psycopg2-binary

# Update requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

---

### Step 4: Update Database Configuration

#### Option A: Update .env file (Recommended)

Create or update `.env` file in project root:

```bash
# .env
ANTHROPIC_API_KEY=your_api_key_here

# Add PostgreSQL connection
DATABASE_URL=postgresql://prediction_user:your_secure_password@localhost:5432/prediction_db

# OR if using default postgres user:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/prediction_db
```

#### Option B: Update database.py directly

Modify `backend/database.py`:

```python
# OLD (line 12-13):
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///predictions.db')

# NEW (add PostgreSQL detection):
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///predictions.db'  # Fallback to SQLite
)
```

---

### Step 5: Initialize PostgreSQL Database

```bash
cd backend
source venv/bin/activate

# Initialize tables in PostgreSQL
python database.py
```

**Output:**
```
Initializing database...
✓ Database tables created successfully!
Database location: postgresql://prediction_user@localhost:5432/prediction_db
```

---

### Step 6: Migrate Existing Data (Optional)

#### If you want to keep your SQLite data:

```python
# Create migration script: migrate_data.py

from database import SessionLocal, Query, Prediction, Source
import sqlite3
import os

def migrate_sqlite_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Check if SQLite database exists
    if not os.path.exists('predictions.db'):
        print("No SQLite database found to migrate")
        return
    
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('predictions.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get PostgreSQL session
    pg_session = SessionLocal()
    
    try:
        # Migrate queries
        print("Migrating queries...")
        sqlite_cursor.execute("SELECT id, query_text, created_at FROM queries")
        for row in sqlite_cursor.fetchall():
            query = Query(id=row[0], query_text=row[1], created_at=row[2])
            pg_session.merge(query)
        
        # Migrate predictions
        print("Migrating predictions...")
        sqlite_cursor.execute("""
            SELECT id, query_id, prediction_text, confidence_score, 
                   key_factors, caveats, model_used, created_at 
            FROM predictions
        """)
        for row in sqlite_cursor.fetchall():
            prediction = Prediction(
                id=row[0],
                query_id=row[1],
                prediction_text=row[2],
                confidence_score=row[3],
                key_factors=row[4],
                caveats=row[5],
                model_used=row[6],
                created_at=row[7]
            )
            pg_session.merge(prediction)
        
        # Migrate sources
        print("Migrating sources...")
        sqlite_cursor.execute("""
            SELECT id, query_id, title, snippet, url, source_name, retrieved_at
            FROM sources
        """)
        for row in sqlite_cursor.fetchall():
            source = Source(
                id=row[0],
                query_id=row[1],
                title=row[2],
                snippet=row[3],
                url=row[4],
                source_name=row[5],
                retrieved_at=row[6]
            )
            pg_session.merge(source)
        
        # Commit all changes
        pg_session.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        pg_session.rollback()
        print(f"❌ Migration failed: {e}")
    finally:
        sqlite_conn.close()
        pg_session.close()

if __name__ == "__main__":
    migrate_sqlite_to_postgresql()
```

**Run migration:**
```bash
python migrate_data.py
```

---

### Step 7: Start Your Application

```bash
# Make sure DATABASE_URL is set in .env
python app.py
```

**Verify it's using PostgreSQL:**
- Check startup logs for PostgreSQL connection
- Make a prediction via API
- Check data in PostgreSQL

---

## 🔍 Verify Migration

### Check PostgreSQL Data:

```bash
# Connect to PostgreSQL
psql prediction_db

# List tables
\dt

# View data
SELECT * FROM queries;
SELECT * FROM predictions;

# Get stats
SELECT COUNT(*) FROM queries;
SELECT AVG(confidence_score) FROM predictions;

# Exit
\q
```

---

## 🔄 Connection String Format

```
postgresql://user:password@host:port/database

Examples:

# Local development
postgresql://prediction_user:mypassword@localhost:5432/prediction_db

# Remote server
postgresql://user:pass@192.168.1.100:5432/prediction_db

# Heroku (provided by Heroku)
postgresql://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname

# AWS RDS
postgresql://admin:pass@mydb.abc123.us-west-2.rds.amazonaws.com:5432/prediction_db
```

---

## 🎯 Code Changes Required

### The Beauty of SQLAlchemy: Almost None!

```python
# database.py - ONLY change needed:
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://prediction_user:password@localhost:5432/prediction_db'
)

# Everything else stays the same!
# ✅ All your models work
# ✅ All your queries work
# ✅ All your relationships work
# ✅ No other code changes needed!
```

**That's it!** SQLAlchemy handles all the differences.

---

## 🔧 PostgreSQL Management

### Useful Commands:

```bash
# Connect to database
psql prediction_db

# Inside psql:

# List databases
\l

# List tables
\dt

# Describe table
\d predictions

# View connections
SELECT * FROM pg_stat_activity WHERE datname = 'prediction_db';

# Database size
SELECT pg_size_pretty(pg_database_size('prediction_db'));

# Table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';

# Backup database
pg_dump prediction_db > backup.sql

# Restore database
psql prediction_db < backup.sql
```

---

## 🐳 Docker Option (Alternative)

### Run PostgreSQL in Docker:

```bash
# Start PostgreSQL container
docker run --name prediction-postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=prediction_db \
  -p 5432:5432 \
  -d postgres:15

# Connection string
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/prediction_db

# Stop container
docker stop prediction-postgres

# Start again
docker start prediction-postgres

# Remove container
docker rm prediction-postgres
```

---

## 🌐 Cloud Hosting Options

### 1. **Heroku Postgres** (Easiest)
```bash
# Add PostgreSQL to Heroku app
heroku addons:create heroku-postgresql:mini

# Get connection string (automatically set as DATABASE_URL)
heroku config:get DATABASE_URL
```

### 2. **AWS RDS**
- Go to AWS Console → RDS
- Create PostgreSQL instance
- Copy endpoint URL
- Format: `postgresql://user:pass@endpoint:5432/dbname`

### 3. **DigitalOcean Managed Database**
- Create database cluster
- Copy connection string
- Use in .env

### 4. **Supabase** (Free PostgreSQL)
- Sign up at supabase.com
- Create project
- Get connection string from settings

---

## 📊 Performance Comparison

### SQLite vs PostgreSQL:

| Metric | SQLite | PostgreSQL |
|--------|--------|------------|
| Concurrent writes | 1 | Unlimited |
| Max connections | 1 | 100+ default |
| Database size | 281 TB | Unlimited |
| Full-text search | Basic | Advanced |
| JSON support | Basic | Advanced |
| Replication | No | Yes |
| Setup time | 0 min | 5-10 min |

---

## 🔒 Security Best Practices

### 1. Use Environment Variables
```bash
# Never hardcode passwords!
# .env
DATABASE_URL=postgresql://user:password@localhost/db
```

### 2. Create Dedicated User
```sql
-- Don't use postgres superuser
CREATE USER prediction_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE prediction_db TO prediction_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prediction_user;
```

### 3. Firewall Rules
```bash
# Only allow local connections in development
# Edit: /etc/postgresql/15/main/postgresql.conf
listen_addresses = 'localhost'

# In production, use specific IPs
listen_addresses = '192.168.1.100'
```

---

## 🐛 Troubleshooting

### Issue: Can't connect to PostgreSQL
```bash
# Check if PostgreSQL is running
pg_isready

# Check if port 5432 is open
lsof -i :5432

# Restart PostgreSQL
brew services restart postgresql@15  # macOS
sudo systemctl restart postgresql    # Linux
```

### Issue: Authentication failed
```bash
# Reset postgres user password
psql postgres
ALTER USER postgres PASSWORD 'newpassword';
```

### Issue: Database doesn't exist
```bash
# List databases
psql -l

# Create database
createdb prediction_db
```

### Issue: Permission denied
```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE prediction_db TO prediction_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO prediction_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO prediction_user;
```

---

## 🎯 Quick Migration Checklist

- [ ] Install PostgreSQL
- [ ] Start PostgreSQL server
- [ ] Create database: `createdb prediction_db`
- [ ] Install driver: `pip install psycopg2-binary`
- [ ] Update .env with DATABASE_URL
- [ ] Initialize tables: `python database.py`
- [ ] (Optional) Migrate SQLite data
- [ ] Test application: `python app.py`
- [ ] Verify data in PostgreSQL: `psql prediction_db`
- [ ] Update documentation
- [ ] Backup SQLite file: `cp predictions.db predictions.db.backup`

---

## 🎉 Benefits After Migration

✅ **Multiple Users** - Handle concurrent requests  
✅ **Better Performance** - Optimized for production  
✅ **Scalability** - Grow without limits  
✅ **Advanced Features** - Full-text search, JSON queries, etc.  
✅ **Production Ready** - Deploy with confidence  
✅ **Cloud Compatible** - Easy to host on Heroku, AWS, etc.  

---

## 📚 Additional Resources

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **SQLAlchemy PostgreSQL**: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- **Heroku Postgres**: https://devcenter.heroku.com/articles/heroku-postgresql
- **PostgreSQL Tutorial**: https://www.postgresqltutorial.com/

---

## 💡 Pro Tips

1. **Keep SQLite for Development**
   - Use SQLite locally (no server needed)
   - Use PostgreSQL in production
   - SQLAlchemy makes this seamless!

2. **Use Connection Pooling**
   ```python
   # In database.py
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,        # Number of connections
       max_overflow=20      # Extra connections if needed
   )
   ```

3. **Regular Backups**
   ```bash
   # Automated backup script
   pg_dump prediction_db > backup_$(date +%Y%m%d).sql
   ```

4. **Monitor Performance**
   ```sql
   -- Slow queries
   SELECT query, mean_exec_time 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   ```

---

## 🚀 You're Ready!

The migration is straightforward thanks to SQLAlchemy. Your code barely changes - just update the connection string and you're running on PostgreSQL!

