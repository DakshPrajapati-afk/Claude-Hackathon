"""
Comprehensive Data Sources Module
Integrates multiple APIs: Reddit, Google, Yahoo Finance, NewsAPI, and web scraping
"""

import os
import requests
from datetime import datetime, timedelta
from textblob import TextBlob
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# Optional imports with fallbacks
try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("⚠️  praw not installed. Install with: pip install praw")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Install with: pip install yfinance")

try:
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️  google-api-python-client not installed. Install with: pip install google-api-python-client")

from newsapi import NewsApiClient


# ============================================================================
# SENTIMENT ANALYSIS
# ============================================================================

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob."""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except:
        return 'neutral'


# ============================================================================
# REDDIT API
# ============================================================================

def fetch_reddit_data(query, limit=10):
    """
    Fetch relevant Reddit posts and comments.
    
    Args:
        query: Search query
        limit: Maximum number of posts to retrieve
        
    Returns:
        List of results with title, snippet, source, url, sentiment
    """
    if not REDDIT_AVAILABLE:
        print("     ⚠️  Reddit API not available (praw not installed)")
        return []
    
    reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    reddit_user_agent = os.getenv('REDDIT_USER_AGENT', 'PolyPredictor/1.0')
    
    if not reddit_client_id or not reddit_client_secret:
        print("     ⚠️  Reddit API keys not configured")
        return []
    
    try:
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )
        
        results = []
        
        # Search relevant subreddits based on query keywords
        subreddits_to_search = get_relevant_subreddits(query)
        
        # Search across selected subreddits
        for subreddit_name in subreddits_to_search:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Search posts in subreddit
                for post in subreddit.search(query, limit=limit // len(subreddits_to_search), time_filter='month'):
                    # Combine title and selftext for analysis
                    text = f"{post.title} {post.selftext[:200]}"
                    
                    results.append({
                        'title': post.title,
                        'snippet': post.selftext[:300] if post.selftext else f"{post.num_comments} comments, Score: {post.score}",
                        'source': f'Reddit r/{subreddit_name}',
                        'url': f"https://reddit.com{post.permalink}",
                        'sentiment': analyze_sentiment(text),
                        'metadata': {
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc).isoformat()
                        }
                    })
                    
                    if len(results) >= limit:
                        break
            except Exception as e:
                print(f"       Error searching r/{subreddit_name}: {e}")
                continue
            
            if len(results) >= limit:
                break
        
        print(f"     ✓ {len(results)} Reddit posts")
        return results[:limit]
        
    except Exception as e:
        print(f"     ❌ Reddit API error: {str(e)}")
        return []


def get_relevant_subreddits(query):
    """Determine relevant subreddits based on query keywords."""
    query_lower = query.lower()
    subreddits = ['all']  # Default to r/all
    
    # Political keywords
    if any(word in query_lower for word in ['election', 'president', 'politics', 'vote', 'trump', 'biden']):
        subreddits = ['politics', 'PoliticalDiscussion', 'neutralpolitics']
    
    # Crypto keywords
    elif any(word in query_lower for word in ['bitcoin', 'crypto', 'ethereum', 'btc', 'eth', 'blockchain']):
        subreddits = ['CryptoCurrency', 'Bitcoin', 'ethereum']
    
    # Stock/finance keywords
    elif any(word in query_lower for word in ['stock', 'market', 'trading', 'invest', 'wallstreet', 'spy', 'tsla']):
        subreddits = ['wallstreetbets', 'stocks', 'investing']
    
    # Tech keywords
    elif any(word in query_lower for word in ['tech', 'ai', 'technology', 'apple', 'google', 'microsoft']):
        subreddits = ['technology', 'tech', 'artificial']
    
    # Prediction markets
    elif 'polymarket' in query_lower or 'prediction' in query_lower:
        subreddits = ['Polymarket', 'PredictionMarkets', 'sportsbook']
    
    return subreddits


# ============================================================================
# GOOGLE CUSTOM SEARCH API
# ============================================================================

def fetch_google_search(query, limit=10):
    """
    Fetch search results from Google Custom Search API.
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of results with title, snippet, source, url, sentiment
    """
    if not GOOGLE_AVAILABLE:
        print("     ⚠️  Google API not available (google-api-python-client not installed)")
        return []
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_cse_id = os.getenv('GOOGLE_CSE_ID')
    
    if not google_api_key or not google_cse_id:
        print("     ⚠️  Google API keys not configured")
        return []
    
    try:
        # Build Google Custom Search service
        service = build("customsearch", "v1", developerKey=google_api_key)
        
        results = []
        
        # Google CSE allows max 10 results per request
        # Make multiple requests if needed
        for start_index in range(1, min(limit, 100), 10):
            try:
                result = service.cse().list(
                    q=query,
                    cx=google_cse_id,
                    num=min(10, limit - len(results)),
                    start=start_index
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')
                        text = f"{title} {snippet}"
                        
                        results.append({
                            'title': title,
                            'snippet': snippet,
                            'source': item.get('displayLink', 'Google Search'),
                            'url': item.get('link', ''),
                            'sentiment': analyze_sentiment(text)
                        })
                        
                        if len(results) >= limit:
                            break
            except Exception as e:
                print(f"       Error in Google search request: {e}")
                break
            
            if len(results) >= limit:
                break
        
        print(f"     ✓ {len(results)} Google results")
        return results
        
    except Exception as e:
        print(f"     ❌ Google API error: {str(e)}")
        return []


# ============================================================================
# YAHOO FINANCE API
# ============================================================================

def fetch_yahoo_finance(query, limit=5):
    """
    Fetch financial data and news from Yahoo Finance.
    
    Args:
        query: Search query (ticker symbol or company name)
        limit: Maximum number of news articles
        
    Returns:
        List of results with financial data and news
    """
    if not YFINANCE_AVAILABLE:
        print("     ⚠️  Yahoo Finance not available (yfinance not installed)")
        return []
    
    # Check if query contains financial keywords
    financial_keywords = ['stock', 'price', 'market', 'trading', '$', 'shares', 'invest']
    if not any(keyword in query.lower() for keyword in financial_keywords):
        return []
    
    try:
        # Try to extract ticker symbols or company names
        tickers = extract_tickers(query)
        
        if not tickers:
            return []
        
        results = []
        
        for ticker in tickers[:3]:  # Limit to 3 tickers
            try:
                stock = yf.Ticker(ticker)
                
                # Get stock info
                info = stock.info
                
                # Get recent news
                news = stock.news if hasattr(stock, 'news') else []
                
                # Add stock info as a result
                if info:
                    price_info = f"Current: ${info.get('currentPrice', 'N/A')}, " \
                                f"Day Change: {info.get('regularMarketChangePercent', 'N/A')}%, " \
                                f"Market Cap: ${info.get('marketCap', 'N/A')}"
                    
                    results.append({
                        'title': f"{ticker} Stock Information",
                        'snippet': price_info,
                        'source': 'Yahoo Finance',
                        'url': f"https://finance.yahoo.com/quote/{ticker}",
                        'sentiment': 'neutral',
                        'metadata': {
                            'type': 'stock_info',
                            'ticker': ticker,
                            'price': info.get('currentPrice'),
                            'change_percent': info.get('regularMarketChangePercent')
                        }
                    })
                
                # Add news articles
                for article in news[:limit]:
                    title = article.get('title', '')
                    summary = article.get('summary', '')
                    text = f"{title} {summary}"
                    
                    results.append({
                        'title': title,
                        'snippet': summary[:300],
                        'source': article.get('publisher', 'Yahoo Finance'),
                        'url': article.get('link', ''),
                        'sentiment': analyze_sentiment(text),
                        'metadata': {
                            'type': 'news',
                            'ticker': ticker,
                            'published': article.get('providerPublishTime')
                        }
                    })
                    
            except Exception as e:
                print(f"       Error fetching {ticker}: {e}")
                continue
        
        if results:
            print(f"     ✓ {len(results)} Yahoo Finance results")
        
        return results
        
    except Exception as e:
        print(f"     ❌ Yahoo Finance error: {str(e)}")
        return []


def extract_tickers(query):
    """Extract potential stock ticker symbols from query."""
    import re
    
    # Common ticker symbols mentioned in queries
    common_tickers = {
        'bitcoin': 'BTC-USD',
        'btc': 'BTC-USD',
        'ethereum': 'ETH-USD',
        'eth': 'ETH-USD',
        'tesla': 'TSLA',
        'apple': 'AAPL',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'amazon': 'AMZN',
        'meta': 'META',
        'nvidia': 'NVDA',
        'spy': 'SPY',
        's&p': 'SPY',
        'dow': 'DIA',
        'nasdaq': 'QQQ'
    }
    
    query_lower = query.lower()
    tickers = []
    
    # Check for common company names/keywords
    for keyword, ticker in common_tickers.items():
        if keyword in query_lower:
            tickers.append(ticker)
    
    # Look for explicit ticker symbols (uppercase 1-5 letters)
    ticker_pattern = r'\b([A-Z]{1,5})\b'
    found_tickers = re.findall(ticker_pattern, query)
    tickers.extend(found_tickers)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for ticker in tickers:
        if ticker not in seen:
            seen.add(ticker)
            unique_tickers.append(ticker)
    
    return unique_tickers


# ============================================================================
# ENHANCED NEWSAPI FUNCTION
# ============================================================================

def fetch_newsapi_articles(query, limit=10):
    """
    Fetch articles from NewsAPI with better error handling.
    """
    news_api_key = os.getenv('NEWS_API_KEY')
    
    if not news_api_key:
        print("     ⚠️  NewsAPI not configured (no API key)")
        return []
    
    try:
        newsapi_client = NewsApiClient(api_key=news_api_key)
        
        # Get articles from last 30 days
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Search everything
        articles = newsapi_client.get_everything(
            q=query,
            from_param=from_date,
            language='en',
            sort_by='relevancy',
            page_size=20
        )
        
        results = []
        query_words = set(query.lower().split())
        
        for article in articles.get('articles', []):
            title = article.get('title', '')
            description = article.get('description', '')
            
            if not title or not description:
                continue
            
            # Calculate relevance
            title_lower = title.lower()
            desc_lower = description.lower()
            relevance = sum(1 for word in query_words if word in title_lower or word in desc_lower)
            
            if relevance > 0 or len(results) < 2:
                text = f"{title} {description}"
                results.append({
                    'title': title,
                    'snippet': description[:200],
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'sentiment': analyze_sentiment(text),
                    'published_at': article.get('publishedAt', ''),
                    'relevance': relevance
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Remove relevance score from output
        for r in results:
            r.pop('relevance', None)
        
        return results[:limit]
        
    except Exception as e:
        print(f"     ❌ NewsAPI error: {str(e)}")
        return []

