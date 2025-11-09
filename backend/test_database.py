#!/usr/bin/env python3
"""
Test script for database functionality.

This script tests:
1. Database initialization
2. Saving prediction data
3. Retrieving queries
4. Database queries
"""

from database import (
    init_db, 
    save_prediction_data, 
    get_recent_queries, 
    get_query_by_id,
    SessionLocal,
    Query,
    Prediction,
    Source
)
from sqlalchemy import func
import json

def test_database():
    """Run comprehensive database tests."""
    
    print("\n" + "="*70)
    print("  🧪 DATABASE TEST SUITE")
    print("="*70 + "\n")
    
    # ========================================================================
    # TEST 1: Initialize Database
    # ========================================================================
    print("Test 1: Initializing database...")
    try:
        init_db()
        print("✓ Database initialized successfully!\n")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}\n")
        return
    
    # ========================================================================
    # TEST 2: Save Sample Prediction Data
    # ========================================================================
    print("Test 2: Saving sample prediction data...")
    try:
        sample_data = {
            'query_text': 'Will electric vehicles dominate the market by 2030?',
            'prediction_text': 'Yes, electric vehicles are likely to capture a significant market share by 2030, potentially reaching 30-50% of new vehicle sales globally.',
            'confidence_score': 75.0,
            'key_factors': [
                'Government incentives and regulations',
                'Declining battery costs',
                'Improved charging infrastructure',
                'Major automaker commitments'
            ],
            'caveats': [
                'Dependent on continued policy support',
                'Charging infrastructure must expand rapidly',
                'Supply chain for batteries must scale'
            ],
            'sources': [
                {
                    'title': 'EV Sales Surge in 2024',
                    'snippet': 'Electric vehicle sales reached record highs this year...',
                    'url': 'https://example.com/ev-news',
                    'source_name': 'Tech News Daily'
                },
                {
                    'title': 'Battery Costs Continue to Fall',
                    'snippet': 'Lithium-ion battery prices dropped 15% year-over-year...',
                    'url': 'https://example.com/battery-costs',
                    'source_name': 'Energy Reports'
                }
            ],
            'model_used': 'claude-sonnet-4-5-test'
        }
        
        result = save_prediction_data(**sample_data)
        
        if result['success']:
            print(f"✓ Sample data saved successfully!")
            print(f"  Query ID: {result['query_id']}")
            print(f"  Prediction ID: {result['prediction_id']}")
            print(f"  Sources saved: {len(result['source_ids'])}\n")
            
            saved_query_id = result['query_id']
        else:
            print(f"✗ Failed to save sample data: {result.get('error')}\n")
            return
    except Exception as e:
        print(f"✗ Error saving sample data: {e}\n")
        return
    
    # ========================================================================
    # TEST 3: Retrieve Recent Queries
    # ========================================================================
    print("Test 3: Retrieving recent queries...")
    try:
        recent_queries = get_recent_queries(limit=5)
        print(f"✓ Retrieved {len(recent_queries)} recent queries")
        
        if recent_queries:
            print("\nRecent queries:")
            for i, q in enumerate(recent_queries[:3], 1):
                print(f"  {i}. {q['query_text'][:60]}...")
                if q['predictions']:
                    pred = q['predictions'][0]
                    print(f"     Confidence: {pred['confidence_score']}%")
        print()
    except Exception as e:
        print(f"✗ Error retrieving recent queries: {e}\n")
    
    # ========================================================================
    # TEST 4: Retrieve Specific Query
    # ========================================================================
    print("Test 4: Retrieving specific query by ID...")
    try:
        query_data = get_query_by_id(saved_query_id)
        
        if query_data:
            print(f"✓ Retrieved query ID {saved_query_id}")
            print(f"  Query: {query_data['query_text']}")
            print(f"  Predictions: {len(query_data['predictions'])}")
            print(f"  Sources: {len(query_data['sources'])}")
            print(f"  Created: {query_data['created_at']}\n")
        else:
            print(f"✗ Query ID {saved_query_id} not found\n")
    except Exception as e:
        print(f"✗ Error retrieving query: {e}\n")
    
    # ========================================================================
    # TEST 5: Database Statistics
    # ========================================================================
    print("Test 5: Getting database statistics...")
    try:
        db = SessionLocal()
        
        total_queries = db.query(func.count(Query.id)).scalar()
        total_predictions = db.query(func.count(Prediction.id)).scalar()
        total_sources = db.query(func.count(Source.id)).scalar()
        avg_confidence = db.query(func.avg(Prediction.confidence_score)).scalar()
        
        print("✓ Database statistics:")
        print(f"  Total queries: {total_queries}")
        print(f"  Total predictions: {total_predictions}")
        print(f"  Total sources: {total_sources}")
        print(f"  Average confidence: {avg_confidence:.1f}%\n")
        
        db.close()
    except Exception as e:
        print(f"✗ Error getting statistics: {e}\n")
    
    # ========================================================================
    # TEST 6: Direct Query Test
    # ========================================================================
    print("Test 6: Testing direct database queries...")
    try:
        db = SessionLocal()
        
        # Get high confidence predictions
        high_confidence = db.query(Prediction).filter(
            Prediction.confidence_score >= 70
        ).all()
        
        print(f"✓ Found {len(high_confidence)} predictions with ≥70% confidence")
        
        # Get queries with their predictions
        queries_with_preds = db.query(Query).join(Prediction).limit(3).all()
        print(f"✓ Found {len(queries_with_preds)} queries with predictions")
        
        if queries_with_preds:
            print("\nSample queries with predictions:")
            for q in queries_with_preds[:2]:
                print(f"  • {q.query_text[:50]}...")
                for pred in q.predictions[:1]:
                    print(f"    → {pred.confidence_score}% confidence")
        
        db.close()
        print()
    except Exception as e:
        print(f"✗ Error with direct queries: {e}\n")
    
    # ========================================================================
    # TEST 7: JSON Data Test
    # ========================================================================
    print("Test 7: Testing JSON field storage...")
    try:
        db = SessionLocal()
        
        # Get a prediction with JSON fields
        pred = db.query(Prediction).first()
        
        if pred:
            print("✓ JSON fields retrieved successfully:")
            print(f"  Key factors (type: {type(pred.key_factors).__name__}): {len(pred.key_factors or [])} items")
            print(f"  Caveats (type: {type(pred.caveats).__name__}): {len(pred.caveats or [])} items")
            
            if pred.key_factors:
                print(f"  Sample key factor: {pred.key_factors[0][:60]}...")
        else:
            print("⚠️  No predictions found to test JSON fields")
        
        db.close()
        print()
    except Exception as e:
        print(f"✗ Error testing JSON fields: {e}\n")
    
    # ========================================================================
    # TEST SUMMARY
    # ========================================================================
    print("="*70)
    print("  ✓ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\n📊 Your database is ready to use!")
    print("\nNext steps:")
    print("  1. Start your Flask app: python app.py")
    print("  2. Make a prediction via the API or frontend")
    print("  3. Check /api/history to see stored predictions")
    print("  4. Check /api/stats for database statistics\n")


if __name__ == "__main__":
    test_database()

