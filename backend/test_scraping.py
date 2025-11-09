#!/usr/bin/env python3
"""
Test script to debug web scraping issues.
Run this to see what's being retrieved.
"""

import sys
sys.path.insert(0, '.')

from app import scrape_web_data, scrape_duckduckgo, fetch_newsapi_articles
import json

def test_scraping(query):
    print("="*70)
    print(f"TESTING WEB SCRAPING FOR: '{query}'")
    print("="*70)
    
    # Test 1: DuckDuckGo
    print("\n1️⃣ Testing DuckDuckGo...")
    try:
        ddg_results = scrape_duckduckgo(query)
        print(f"   Results: {len(ddg_results)}")
        if ddg_results:
            print(f"   Sample: {ddg_results[0].get('title', 'No title')[:60]}...")
        else:
            print("   ❌ NO RESULTS FROM DUCKDUCKGO")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: NewsAPI
    print("\n2️⃣ Testing NewsAPI...")
    try:
        news_results = fetch_newsapi_articles(query)
        print(f"   Results: {len(news_results)}")
        if news_results:
            print(f"   Sample: {news_results[0].get('title', 'No title')[:60]}...")
        else:
            print("   ⚠️  No results (may need API key)")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Full aggregation
    print("\n3️⃣ Testing Full Aggregation (scrape_web_data)...")
    try:
        all_results = scrape_web_data(query)
        print(f"\n   FINAL RESULTS: {len(all_results)}")
        
        if all_results:
            print("\n   📊 Results breakdown:")
            for i, result in enumerate(all_results[:3], 1):
                print(f"\n   {i}. {result.get('title', 'No title')[:60]}")
                print(f"      Source: {result.get('source', 'Unknown')}")
                print(f"      Quality: {result.get('quality_score', 'N/A')}")
                print(f"      Badge: {result.get('reputation_badge', 'N/A')}")
        else:
            print("\n   ❌ ZERO RESULTS AFTER AGGREGATION")
            print("   This is why you're getting 'no web data provided'")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "2024 presidential election"
    
    test_scraping(query)
    
    print("\n" + "="*70)
    print("DIAGNOSIS:")
    print("="*70)
    print("If you see:")
    print("  ✅ Results from DuckDuckGo but 0 final results:")
    print("     → Quality filtering is too strict")
    print("  ❌ No results from DuckDuckGo:")
    print("     → DuckDuckGo scraping is broken")
    print("  ⚠️  Error messages:")
    print("     → Check error details above")
    print("="*70)

