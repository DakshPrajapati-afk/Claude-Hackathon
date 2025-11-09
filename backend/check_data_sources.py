#!/usr/bin/env python3
"""
Data Source Verification Script
Run this to check which data sources are actually being used
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../.env')

print("=" * 60)
print("🔍 DATA SOURCE VERIFICATION")
print("=" * 60)

# Check API keys in .env
api_keys_config = {
    'Google Custom Search': {
        'keys': ['GOOGLE_API_KEY', 'GOOGLE_CSE_ID'],
        'required': True
    },
    'NewsAPI': {
        'keys': ['NEWS_API_KEY'],
        'required': True
    },
    'Reddit': {
        'keys': ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT'],
        'required': True
    },
    'Yahoo Finance': {
        'keys': [],
        'required': False
    },
    'Anthropic (Claude)': {
        'keys': ['ANTHROPIC_API_KEY'],
        'required': True
    }
}

print("\n📋 API KEYS STATUS:")
print("-" * 60)
all_keys_present = True
for service, config in api_keys_config.items():
    keys = config['keys']
    if not keys:
        print(f"  ✅ {service}: No key required")
    else:
        present_keys = [key for key in keys if os.getenv(key)]
        missing_keys = [key for key in keys if not os.getenv(key)]
        
        if not missing_keys:
            print(f"  ✅ {service}: All keys configured")
            for key in keys:
                value = os.getenv(key, '')
                masked = value[:10] + '...' if len(value) > 10 else value
                print(f"      - {key}={masked}")
        else:
            status = "⚠️" if not config['required'] else "❌"
            print(f"  {status} {service}: Missing keys")
            for key in missing_keys:
                print(f"      - {key}: NOT FOUND")
            if config['required']:
                all_keys_present = False

print("\n" + "=" * 60)
print("🔧 IMPLEMENTATION STATUS:")
print("=" * 60)

# Check if functions are implemented in app.py
try:
    with open('app.py', 'r') as f:
        app_code = f.read()
    
    checks = {
        'Google Search': 'fetch_google_search',
        'NewsAPI': 'fetch_newsapi',
        'Reddit': 'fetch_reddit_data',
        'Yahoo Finance': 'fetch_yahoo_finance',
        'MarketWatch': 'fetch_marketwatch_news',
    }
    
    all_implemented = True
    for service, function_name in checks.items():
        if function_name in app_code:
            print(f"  ✅ {service}: {function_name}() is called")
        else:
            print(f"  ❌ {service}: {function_name}() NOT found in app.py")
            all_implemented = False
    
    print("\n" + "=" * 60)
    print("📦 DEPENDENCIES CHECK:")
    print("=" * 60)
    
    dependencies = {
        'praw': 'Reddit API',
        'yfinance': 'Yahoo Finance',
        'google.auth': 'Google API',
        'anthropic': 'Claude API',
        'newsapi': 'NewsAPI'
    }
    
    all_deps_installed = True
    for module, service in dependencies.items():
        try:
            __import__(module.split('.')[0])
            print(f"  ✅ {service}: {module} installed")
        except ImportError:
            print(f"  ❌ {service}: {module} NOT installed")
            all_deps_installed = False
    
    print("\n" + "=" * 60)
    print("🎯 OVERALL STATUS:")
    print("=" * 60)
    
    if all_keys_present and all_implemented and all_deps_installed:
        print("  ✅ ALL SYSTEMS GO! All data sources are ready.")
    else:
        print("  ⚠️  ISSUES DETECTED:")
        if not all_keys_present:
            print("     - Some required API keys are missing")
        if not all_implemented:
            print("     - Some functions are not implemented in app.py")
        if not all_deps_installed:
            print("     - Some dependencies are not installed")
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("=" * 60)
    print("  1. Start backend: python app.py")
    print("  2. Make test query:")
    print("     curl -X POST http://localhost:5001/api/predict \\")
    print("       -H 'Content-Type: application/json' \\")
    print("       -d '{\"query\": \"Will Bitcoin reach $100k?\"}'")
    print("  3. Check console output for source breakdown")
    print("=" * 60)

except FileNotFoundError:
    print("  ❌ app.py not found. Are you in the backend directory?")
except Exception as e:
    print(f"  ❌ Error checking implementation: {e}")

