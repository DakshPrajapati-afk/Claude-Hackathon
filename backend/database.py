"""
Database models and configuration for storing prediction data.

This module defines the database schema for storing:
- User queries
- Predictions and confidence scores
- Sources (web data)
- Analysis history
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Database URL - Use SQLite for development, PostgreSQL for production
# To use PostgreSQL: postgresql://username:password@localhost/dbname
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///predictions.db')

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create declarative base
Base = declarative_base()

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Query(Base):
    """
    Stores user queries and metadata.
    """
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="query", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="query", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Query(id={self.id}, query='{self.query_text[:50]}...', created_at={self.created_at})>"


class Prediction(Base):
    """
    Stores AI-generated predictions with confidence scores.
    """
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('queries.id'), nullable=False)
    
    # Prediction details
    prediction_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-100
    
    # Additional analysis (stored as JSON)
    key_factors = Column(JSON)  # List of key factors
    caveats = Column(JSON)      # List of caveats
    
    # Metadata
    model_used = Column(String(100))  # e.g., "claude-sonnet-4-5"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query = relationship("Query", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, confidence={self.confidence_score}%, query_id={self.query_id})>"


class Source(Base):
    """
    Stores web sources used for predictions.
    """
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('queries.id'), nullable=False)
    
    # Source details
    title = Column(Text, nullable=False)
    snippet = Column(Text)
    url = Column(Text)
    source_name = Column(String(255))  # e.g., "CNN", "BBC"
    
    # Metadata
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query = relationship("Query", back_populates="sources")
    
    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title[:50]}...', query_id={self.query_id})>"


class MarketData(Base):
    """
    Stores Polymarket prediction market data.
    """
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('queries.id'), nullable=True)
    
    # Market details
    question = Column(Text, nullable=False)
    slug = Column(String(255), index=True)
    market_url = Column(Text)
    
    # Odds and metrics
    yes_price = Column(Float)   # 0.0 to 1.0
    no_price = Column(Float)    # 0.0 to 1.0
    volume = Column(String(50))
    liquidity = Column(String(50))
    end_date = Column(String(50))
    
    # Metadata
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData(id={self.id}, question='{self.question[:50]}...', yes={self.yes_price})>"


class NewsArticle(Base):
    """
    Stores news articles used for analysis.
    """
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('queries.id'), nullable=True)
    
    # Article details
    title = Column(Text, nullable=False)
    source = Column(String(255))
    date = Column(String(50))
    summary = Column(Text)
    sentiment = Column(String(20))  # 'positive', 'negative', 'neutral'
    
    # Metadata
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', sentiment={self.sentiment})>"


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize database by creating all tables.
    Call this once when setting up the application.
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def get_db():
    """
    Get database session. Use with context manager:
    
    with get_db() as db:
        # perform database operations
        pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_prediction_data(query_text, prediction_text, confidence_score, 
                         key_factors, caveats, sources, model_used="claude-sonnet-4-5"):
    """
    Save a complete prediction with all related data.
    
    Parameters:
    -----------
    query_text : str
        The user's original query
    prediction_text : str
        The AI-generated prediction
    confidence_score : float
        Confidence score (0-100)
    key_factors : list
        List of key factors
    caveats : list
        List of caveats
    sources : list of dict
        List of source dictionaries with 'title' and 'snippet'
    model_used : str
        Name of the AI model used
    
    Returns:
    --------
    dict : Dictionary with created record IDs
    """
    db = SessionLocal()
    try:
        # Create query record
        query = Query(query_text=query_text)
        db.add(query)
        db.flush()  # Get the query ID
        
        # Create prediction record
        prediction = Prediction(
            query_id=query.id,
            prediction_text=prediction_text,
            confidence_score=confidence_score,
            key_factors=key_factors,
            caveats=caveats,
            model_used=model_used
        )
        db.add(prediction)
        
        # Create source records
        source_ids = []
        for source_data in sources:
            source = Source(
                query_id=query.id,
                title=source_data.get('title', ''),
                snippet=source_data.get('snippet', ''),
                url=source_data.get('url', ''),
                source_name=source_data.get('source_name', '')
            )
            db.add(source)
            db.flush()
            source_ids.append(source.id)
        
        # Commit all changes
        db.commit()
        
        return {
            'query_id': query.id,
            'prediction_id': prediction.id,
            'source_ids': source_ids,
            'success': True
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error saving prediction data: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def get_recent_queries(limit=10):
    """
    Get the most recent queries with their predictions.
    
    Parameters:
    -----------
    limit : int
        Number of queries to return
    
    Returns:
    --------
    list : List of query dictionaries
    """
    db = SessionLocal()
    try:
        queries = db.query(Query).order_by(Query.created_at.desc()).limit(limit).all()
        
        results = []
        for query in queries:
            results.append({
                'id': query.id,
                'query_text': query.query_text,
                'created_at': query.created_at.isoformat(),
                'predictions': [
                    {
                        'prediction_text': pred.prediction_text,
                        'confidence_score': pred.confidence_score,
                        'key_factors': pred.key_factors,
                        'caveats': pred.caveats
                    }
                    for pred in query.predictions
                ]
            })
        
        return results
        
    finally:
        db.close()


def get_query_by_id(query_id):
    """
    Get a specific query with all related data.
    
    Parameters:
    -----------
    query_id : int
        The query ID
    
    Returns:
    --------
    dict : Complete query data with predictions and sources
    """
    db = SessionLocal()
    try:
        query = db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            return None
        
        return {
            'id': query.id,
            'query_text': query.query_text,
            'created_at': query.created_at.isoformat(),
            'predictions': [
                {
                    'id': pred.id,
                    'prediction_text': pred.prediction_text,
                    'confidence_score': pred.confidence_score,
                    'key_factors': pred.key_factors,
                    'caveats': pred.caveats,
                    'model_used': pred.model_used,
                    'created_at': pred.created_at.isoformat()
                }
                for pred in query.predictions
            ],
            'sources': [
                {
                    'id': source.id,
                    'title': source.title,
                    'snippet': source.snippet,
                    'url': source.url,
                    'source_name': source.source_name
                }
                for source in query.sources
            ]
        }
        
    finally:
        db.close()


if __name__ == "__main__":
    """
    Run this file directly to initialize the database.
    """
    print("Initializing database...")
    init_db()
    print("\n✓ Database setup complete!")
    print(f"Database location: {DATABASE_URL}")

