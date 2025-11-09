#!/usr/bin/env python3
"""
AI-Powered Polymarket Research Assistant

This application serves as an intelligent research tool that helps users analyze
prediction markets on Polymarket. When a user provides a topic of interest, the 
system automatically:
1. Searches for relevant prediction markets
2. Gathers contextual news and information
3. Performs sentiment analysis
4. Builds comprehensive prediction reasoning
5. Presents actionable insights

Author: Research Assistant Team
Purpose: Democratize access to prediction market analysis
"""

# ============================================================================
# IMPORTS
# ============================================================================

import requests      # For making HTTP requests to APIs (Polymarket, NewsAPI)
import json          # For parsing JSON responses from APIs
from datetime import datetime  # For timestamping analysis outputs
import re            # For regular expression pattern matching (future use)

# Sentiment Analysis
try:
    from textblob import TextBlob  # For automatic sentiment analysis of text
    TEXTBLOB_AVAILABLE = True
except ImportError:
    # TextBlob not installed - will fall back to neutral sentiment
    TEXTBLOB_AVAILABLE = False
    print("⚠️  TextBlob not installed. Install with: pip install textblob")
    print("   Sentiment analysis will use fallback method.\n")

# ============================================================================
# STEP 1: SEARCH POLYMARKET FOR RELEVANT MARKETS
# ============================================================================

def search_polymarket_markets(query):
    """
    Search Polymarket API for prediction markets related to the user's query.
    
    This function queries the Polymarket Gamma API to retrieve active prediction
    markets and filters them based on relevance to the user's search query. The
    relevance is determined by checking if any words from the query appear in
    the market's question or description.
    
    Parameters:
    -----------
    query : str
        The user's search query (e.g., "Trump 2024", "Bitcoin $100k")
    
    Returns:
    --------
    list of dict
        A list of up to 5 most relevant markets, where each market is a dictionary
        containing:
        - question (str): The prediction market question
        - slug (str): URL-friendly identifier for the market
        - yes_price (float): Current probability/price for YES outcome (0-1)
        - no_price (float): Current probability/price for NO outcome (0-1)
        - volume (str): Total trading volume in the market
        - liquidity (str): Available liquidity in the market
        - end_date (str): When the market closes/resolves
        - url (str): Direct link to the market on Polymarket
        
        Returns empty list if no markets found or API fails
    
    Algorithm:
    ----------
    1. Query Polymarket API for active markets (limit 10 for performance)
    2. Parse each market's question and description
    3. Check if any word from user query appears in market text
    4. Collect matching markets with relevant data points
    5. Return top 5 most relevant matches
    
    Error Handling:
    ---------------
    - Network errors: Caught and logged, returns empty list
    - API errors: Caught and logged, returns empty list
    - Timeout errors: Request times out after 10 seconds
    """
    try:
        # Polymarket Gamma API endpoint for retrieving market data
        # This is their public API for accessing prediction market information
        url = f"https://gamma-api.polymarket.com/markets"
        
        # Query parameters to filter API results
        params = {
            'limit': 10,      # Request 10 markets (balance between coverage and speed)
            'active': 'true'  # Only get currently active markets (not closed/resolved)
        }
        
        # Make GET request to Polymarket API with 10-second timeout
        # Timeout prevents hanging if API is slow or unresponsive
        response = requests.get(url, params=params, timeout=10)
        
        # Check if API request was successful (HTTP 200 OK)
        if response.status_code == 200:
            # Parse JSON response containing market data
            markets = response.json()
            
            # Convert user query to lowercase for case-insensitive matching
            query_lower = query.lower()
            
            # List to store markets that match the user's query
            relevant_markets = []
            
            # Iterate through each market returned by the API
            for market in markets:
                # Extract market question and description, convert to lowercase
                # Use .get() with empty string default to handle missing fields safely
                question = market.get('question', '').lower()
                description = market.get('description', '').lower()
                
                # Relevance algorithm: Check if ANY word from the query appears
                # in either the market question or description
                # This is a simple but effective keyword matching approach
                # Split query into individual words and check each one
                if any(word in question or word in description 
                       for word in query_lower.split()):
                    
                    # Market is relevant - extract and structure the key data points
                    relevant_markets.append({
                        'question': market.get('question'),  # Main market question
                        'slug': market.get('slug'),          # URL identifier
                        
                        # outcomePrices is an array: [YES price, NO price]
                        # These represent the current probability (0.0 to 1.0)
                        # Default to ['0', '0'] if missing to prevent index errors
                        'yes_price': float(market.get('outcomePrices', ['0', '0'])[0]),
                        'no_price': float(market.get('outcomePrices', ['0', '0'])[1]),
                        
                        # Trading metrics (as strings from API)
                        'volume': market.get('volume', '0'),        # Total $ traded
                        'liquidity': market.get('liquidity', '0'),  # Available $ for trading
                        'end_date': market.get('endDate', ''),      # Market resolution date
                        
                        # Construct direct URL to market on Polymarket website
                        'url': f"https://polymarket.com/event/{market.get('slug', '')}"
                    })
            
            # Return only top 5 most relevant markets to keep output focused
            # Slice notation [:5] safely handles cases with fewer than 5 markets
            return relevant_markets[:5]
        
        # If API returned non-200 status code, return empty list
        return []
        
    except Exception as e:
        # Catch all exceptions (network errors, JSON parsing errors, etc.)
        # Print user-friendly error message and return empty list to fail gracefully
        print(f"⚠️  Could not access Polymarket API: {e}")
        return []

def calculate_prediction_odds(news_items):
    """
    Calculate dynamic prediction odds based on news sentiment and other factors.
    
    This function analyzes news data to generate realistic prediction market odds
    instead of using hardcoded values. The odds are influenced by:
    - Overall sentiment (positive/negative/neutral)
    - Sentiment strength (how strong the sentiment is)
    - News volume (more articles = more confidence in the signal)
    - Sentiment consistency (agreement across sources)
    
    Parameters:
    -----------
    news_items : list of dict
        List of news articles with sentiment labels
    
    Returns:
    --------
    tuple: (yes_price, no_price, confidence_level)
        yes_price : float
            Probability for YES outcome (0.0 to 1.0)
        no_price : float
            Probability for NO outcome (0.0 to 1.0)
        confidence_level : str
            How confident the prediction is ('low', 'medium', 'high')
    
    Algorithm:
    ----------
    1. Start with neutral baseline (50/50)
    2. Calculate sentiment score (-1 to +1)
    3. Adjust odds based on sentiment strength
    4. Scale adjustment by news volume (more news = stronger signal)
    5. Cap odds at reasonable bounds (20-80%)
    6. Determine confidence level based on factors
    
    Examples:
    ---------
    - 5 positive, 0 negative, 0 neutral → 72% YES (strong signal)
    - 2 positive, 2 negative, 1 neutral → 50% YES (mixed/neutral)
    - 0 positive, 4 negative, 1 neutral → 28% YES (strong NO signal)
    - 1 positive, 0 negative, 0 neutral → 58% YES (weak positive signal)
    """
    # Start with neutral baseline (50% YES, 50% NO)
    base_yes_prob = 0.50
    
    # Handle edge case: no news available
    if not news_items:
        return base_yes_prob, 1 - base_yes_prob, 'low'
    
    # Count sentiment types
    sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    for item in news_items:
        sentiment = item.get('sentiment', 'neutral')
        sentiments[sentiment] += 1
    
    total_articles = len(news_items)
    
    # Calculate raw sentiment score (-1 to +1)
    # Positive articles push toward YES, negative toward NO
    if total_articles > 0:
        sentiment_score = (sentiments['positive'] - sentiments['negative']) / total_articles
    else:
        sentiment_score = 0.0
    
    # ========================================================================
    # CALCULATE ODDS ADJUSTMENT
    # ========================================================================
    # Sentiment score ranges from -1 to +1
    # We'll allow it to shift odds by up to ±30 percentage points
    # This creates a range from 20% to 80% (avoiding extreme 0% or 100%)
    
    # Scale sentiment to percentage point adjustment
    # -1.0 sentiment → -30 points (50% becomes 20%)
    # +1.0 sentiment → +30 points (50% becomes 80%)
    # 0.0 sentiment → 0 points (stays at 50%)
    max_adjustment = 0.30  # Maximum 30 percentage point shift
    
    # Apply volume scaling: more articles = more confident in adjustment
    # With 1 article, use only 40% of adjustment
    # With 5+ articles, use 100% of adjustment
    volume_factor = min(1.0, 0.4 + (total_articles * 0.12))
    
    # Calculate final adjustment
    adjustment = sentiment_score * max_adjustment * volume_factor
    
    # Apply adjustment to base probability
    yes_price = base_yes_prob + adjustment
    
    # Ensure odds stay within reasonable bounds [0.15, 0.85]
    # Markets rarely go below 15% or above 85% (too extreme)
    yes_price = max(0.15, min(0.85, yes_price))
    no_price = 1.0 - yes_price
    
    # ========================================================================
    # CALCULATE CONFIDENCE LEVEL
    # ========================================================================
    # Confidence is based on:
    # 1. How many articles we have (more = higher confidence)
    # 2. How consistent the sentiment is (all positive/negative = high confidence)
    # 3. How strong the sentiment is
    
    # Calculate sentiment consistency (0 to 1)
    # If all articles agree, consistency is high
    # If mixed, consistency is low
    dominant_sentiment = max(sentiments['positive'], sentiments['negative'], sentiments['neutral'])
    consistency = dominant_sentiment / total_articles if total_articles > 0 else 0
    
    # Determine confidence level
    if total_articles >= 5 and consistency >= 0.6 and abs(sentiment_score) > 0.3:
        confidence = 'high'  # Many articles, consistent sentiment, strong signal
    elif total_articles >= 3 and consistency >= 0.5:
        confidence = 'medium'  # Decent articles, somewhat consistent
    else:
        confidence = 'low'  # Few articles or inconsistent sentiment
    
    return yes_price, no_price, confidence

def create_mock_market(query, news_items=None):
    """
    Create a mock/simulated prediction market based on the user's query.
    
    This function serves as a fallback when the Polymarket API is unavailable,
    returns no results, or for demonstration purposes. It generates a realistic
    mock market with DYNAMIC odds calculated from news sentiment analysis.
    
    Parameters:
    -----------
    query : str
        The user's query topic (e.g., "Trump 2024", "Bitcoin $100k")
    news_items : list of dict, optional
        List of news articles to analyze for calculating odds
        If None, uses baseline 50/50 odds
    
    Returns:
    --------
    dict
        A mock market dictionary with the same structure as real market data:
        - question: Generic question based on query
        - slug: URL-friendly version of query
        - yes_price: DYNAMICALLY calculated based on news sentiment
        - no_price: DYNAMICALLY calculated (1 - yes_price)
        - volume: Simulated trading volume (varies by confidence)
        - liquidity: Simulated available liquidity
        - end_date: Default end date (end of year)
        - url: Generic Polymarket homepage link
    
    Dynamic Odds Calculation:
    -------------------------
    If news_items are provided, odds are calculated using:
    - Sentiment analysis (positive/negative/neutral balance)
    - News volume (more articles = stronger signal)
    - Sentiment consistency (agreement across sources)
    
    This creates realistic, data-driven odds instead of hardcoded 55/45!
    
    Use Case:
    ---------
    This allows the application to still provide a prediction analysis even when
    the API is down, during development, or for topics without existing markets.
    The mock data now reflects actual sentiment analysis results.
    """
    # Calculate dynamic odds based on news sentiment
    if news_items:
        yes_price, no_price, confidence = calculate_prediction_odds(news_items)
        
        # Vary volume and liquidity based on confidence level
        # High confidence markets attract more trading
        volume_map = {
            'high': '5000000',    # $5M for high confidence
            'medium': '2500000',  # $2.5M for medium confidence  
            'low': '1000000'      # $1M for low confidence
        }
        liquidity_map = {
            'high': '800000',     # $800K
            'medium': '500000',   # $500K
            'low': '250000'       # $250K
        }
        
        volume = volume_map.get(confidence, '2500000')
        liquidity = liquidity_map.get(confidence, '500000')
    else:
        # Fallback if no news provided: use neutral baseline
        yes_price = 0.50
        no_price = 0.50
        volume = '1500000'
        liquidity = '300000'
    
    return {
        # Create a generic question from the query
        'question': f"Will {query} happen?",
        
        # Generate URL-friendly slug by lowercasing and replacing spaces with hyphens
        'slug': query.lower().replace(' ', '-'),
        
        # DYNAMIC odds calculated from sentiment analysis!
        'yes_price': yes_price,
        'no_price': no_price,
        
        # Market metrics that vary based on confidence
        'volume': volume,
        'liquidity': liquidity,
        
        # Set far future end date so market appears "active"
        'end_date': '2025-12-31',
        
        # Link to Polymarket homepage since we don't have a specific market
        'url': 'https://polymarket.com'
    }

# ============================================================================
# STEP 2: GATHER NEWS AND CONTEXT USING WEB SEARCH
# ============================================================================

def analyze_text_sentiment(text):
    """
    Analyze sentiment of text using TextBlob (if available).
    
    This function uses TextBlob's built-in sentiment analysis to classify
    text as positive, negative, or neutral based on polarity scores.
    
    Parameters:
    -----------
    text : str
        The text to analyze (usually article title + summary)
    
    Returns:
    --------
    str
        One of: 'positive', 'negative', or 'neutral'
    
    Algorithm:
    ----------
    TextBlob returns polarity from -1 (negative) to +1 (positive)
    We use thresholds to classify:
    - polarity > 0.1: positive (clearly positive language)
    - polarity < -0.1: negative (clearly negative language)  
    - else: neutral (mixed or neutral language)
    
    Thresholds Rationale:
    ---------------------
    The ±0.1 threshold prevents slight variations from being misclassified.
    Articles need clear positive or negative language to be labeled as such.
    
    Fallback:
    ---------
    If TextBlob is not installed, returns 'neutral' for all text.
    """
    # Check if TextBlob is available
    if not TEXTBLOB_AVAILABLE:
        return 'neutral'  # Fallback to neutral if library not installed
    
    try:
        # Create TextBlob object and analyze sentiment
        blob = TextBlob(text)
        
        # Get polarity score (-1 to +1)
        # Polarity: -1 = very negative, 0 = neutral, +1 = very positive
        polarity = blob.sentiment.polarity
        
        # Classify based on thresholds
        if polarity > 0.1:
            return 'positive'  # Clearly positive sentiment
        elif polarity < -0.1:
            return 'negative'  # Clearly negative sentiment
        else:
            return 'neutral'   # Neutral or mixed sentiment
            
    except Exception as e:
        # If TextBlob analysis fails for any reason, default to neutral
        # This prevents crashes from malformed text or encoding issues
        return 'neutral'

def search_news_simple(query):
    """
    Simulate news search with pre-populated mock data for demonstration purposes.
    
    This function provides realistic sample news articles for common query topics.
    In a production environment, this would be replaced with actual API calls to
    NewsAPI, web scraping, or AI-powered web search capabilities.
    
    Parameters:
    -----------
    query : str
        The user's search query topic
    
    Returns:
    --------
    list of dict
        A list of mock news articles, each containing:
        - title (str): Article headline
        - source (str): Publication/news source name
        - date (str): Publication date in YYYY-MM-DD format
        - summary (str): Brief article summary or description
        - sentiment (str): Article sentiment ('positive', 'negative', or 'neutral')
    
    Algorithm:
    ----------
    1. Check if any keyword from mock_news dict appears in query
    2. Return corresponding pre-built news articles
    3. Fall back to generic news if no match found
    
    Note:
    -----
    The sentiment labels are manually assigned based on article content.
    In production, use NLP sentiment analysis (VADER, TextBlob, or LLM-based).
    """
    # Dictionary of pre-built mock news for common query topics
    # Each topic has 4-5 articles with varied sentiments for realistic analysis
    mock_news = {
        # Trump-related prediction markets (election, political events)
        'trump': [
            # Positive sentiment article - polling data
            {
                'title': 'Latest polls show Trump leading in swing states',
                'source': 'Political Analysis Weekly',
                'date': '2025-11-07',
                'summary': 'Recent polling data indicates a 3-point lead in Pennsylvania',
                'sentiment': 'positive'  # Favorable polling = positive
            },
            # Positive sentiment article - fundraising success
            {
                'title': 'Campaign fundraising reaches record levels',
                'source': 'Campaign Finance Tracker',
                'date': '2025-11-06',
                'summary': 'Q4 fundraising exceeded expectations with $50M raised',
                'sentiment': 'positive'  # Strong fundraising = positive
            },
            # Neutral sentiment article - mixed reviews
            {
                'title': 'Debate performance gets mixed reviews',
                'source': 'Media Watch',
                'date': '2025-11-05',
                'summary': 'Analysts divided on debate effectiveness',
                'sentiment': 'neutral'  # No clear positive/negative
            },
            # Negative sentiment article - legal issues
            {
                'title': 'Legal proceedings continue with uncertain impact',
                'source': 'Legal News Daily',
                'date': '2025-11-04',
                'summary': 'Court cases ongoing, political impact unclear',
                'sentiment': 'negative'  # Legal challenges = negative
            },
            # Neutral sentiment article - economic factors
            {
                'title': 'Economic indicators show mixed signals',
                'source': 'Economic Forecast',
                'date': '2025-11-03',
                'summary': 'GDP growth positive but inflation concerns remain',
                'sentiment': 'neutral'  # Mixed economic news
            }
        ],
        
        # Bitcoin/crypto-related prediction markets (price predictions)
        'bitcoin': [
            # Positive sentiment - price surge
            {
                'title': 'Bitcoin surges past $95k on institutional demand',
                'source': 'Crypto News Network',
                'date': '2025-11-07',
                'summary': 'Major institutional buyers enter market',
                'sentiment': 'positive'  # Price increase = positive
            },
            # Positive sentiment - ETF inflows
            {
                'title': 'ETF inflows hit record highs',
                'source': 'Financial Times',
                'date': '2025-11-06',
                'summary': 'Bitcoin ETFs see $1B in weekly inflows',
                'sentiment': 'positive'  # Strong inflows = positive
            },
            # Positive sentiment - regulatory news
            {
                'title': 'Regulatory clarity boosts confidence',
                'source': 'Regulatory Watch',
                'date': '2025-11-05',
                'summary': 'New framework provides certainty for crypto markets',
                'sentiment': 'positive'  # Favorable regulation = positive
            },
            # Positive sentiment - technical analysis
            {
                'title': 'Technical analysts predict breakout',
                'source': 'Technical Analysis Daily',
                'date': '2025-11-04',
                'summary': 'Chart patterns suggest move toward $100k',
                'sentiment': 'positive'  # Bullish prediction = positive
            }
        ],
        
        # Default fallback for any other query
        'default': [
            {
                # Generic article using the query topic
                'title': f'Recent developments in {query}',
                'source': 'News Aggregator',
                'date': '2025-11-07',
                'summary': f'Latest updates and analysis on {query}',
                'sentiment': 'neutral'  # Generic = neutral
            }
        ]
    }
    
    # Match user query to mock data by keyword
    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()
    
    # Iterate through mock news dictionary keys (topics)
    for key in mock_news:
        # If topic keyword found in query, return that topic's news
        if key in query_lower:
            return mock_news[key]
    
    # If no match found, return generic default news
    return mock_news['default']

def search_with_newsapi(query, api_key):
    """
    Fetch real news articles using the NewsAPI service.
    
    This function queries NewsAPI.org to retrieve recent, relevant news articles
    about the user's query topic. It provides actual, up-to-date news when an
    API key is available.
    
    Parameters:
    -----------
    query : str
        The search query/topic to find news about
    api_key : str or None
        NewsAPI.org API key (get free key at https://newsapi.org)
        If None, function returns None immediately
    
    Returns:
    --------
    list of dict or None
        If successful: List of articles with same structure as search_news_simple()
        If failed: None (triggers fallback to mock data)
        
        Each article dict contains:
        - title: Article headline
        - source: Publication name
        - date: Publication date (YYYY-MM-DD format)
        - summary: Article description/excerpt
        - sentiment: Automatically analyzed using TextBlob (positive/negative/neutral)
    
    API Documentation:
    ------------------
    NewsAPI endpoint: /v2/everything
    Returns news from ~80,000 sources worldwide
    Free tier: 100 requests/day, 30 days of history
    
    Sentiment Analysis:
    -------------------
    Uses TextBlob to analyze sentiment of (title + description)
    - If TextBlob is installed: Real sentiment classification
    - If TextBlob is not installed: Falls back to 'neutral' for all articles
    
    Error Handling:
    ---------------
    - Returns None if no API key provided
    - Returns None on network errors
    - Returns None on API errors (bad key, rate limit, etc.)
    - Calling code should fall back to search_news_simple() when None returned
    - Sentiment analysis failures default to 'neutral' (won't crash)
    """
    # Check if API key is provided
    if not api_key:
        return None  # No key = can't make API call
    
    try:
        # NewsAPI "everything" endpoint - searches all articles
        url = "https://newsapi.org/v2/everything"
        
        # Build query parameters
        params = {
            'q': query,                    # Search query
            'sortBy': 'publishedAt',       # Sort by most recent first
            'apiKey': api_key,             # Authentication
            'language': 'en',              # English articles only
            'pageSize': 10                 # Return up to 10 articles
        }
        
        # Make API request with 10-second timeout
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            # Extract articles array from JSON response
            articles = response.json().get('articles', [])
            
            # Transform NewsAPI format into our standardized format
            # Use list comprehension to process each article
            processed_articles = []
            for a in articles:
                # Combine title and description for more accurate sentiment analysis
                # Title alone might miss context; description provides more detail
                text_to_analyze = a['title'] + ' ' + a.get('description', '')
                
                processed_articles.append({
                    'title': a['title'],                           # Article headline
                    'source': a['source']['name'],                 # Publication name
                    'date': a['publishedAt'][:10],                 # Extract YYYY-MM-DD from timestamp
                    'summary': a.get('description', ''),           # Article description (may be missing)
                    'sentiment': analyze_text_sentiment(text_to_analyze)  # Real sentiment analysis!
                })
            
            return processed_articles
        
        # Non-200 status code = API error
        return None
        
    except Exception as e:
        # Catch all errors (network, timeout, JSON parsing, etc.)
        print(f"⚠️  NewsAPI error: {e}")
        return None

# ============================================================================
# STEP 3: AI ANALYSIS - BUILD PREDICTION REASONING
# ============================================================================

def analyze_sentiment(news_items):
    """
    Analyze and aggregate sentiment across multiple news articles.
    
    This function takes a collection of news articles (each with a sentiment label)
    and computes an overall sentiment classification and numerical score. This helps
    quantify the general "mood" of recent news about a topic.
    
    Parameters:
    -----------
    news_items : list of dict
        List of news articles, each containing a 'sentiment' key
        with value 'positive', 'negative', or 'neutral'
    
    Returns:
    --------
    tuple: (overall_sentiment, sentiment_score)
        overall_sentiment : str
            One of: 'positive', 'negative', or 'neutral'
            Based on the aggregate balance of sentiments
        sentiment_score : float
            Normalized score from 0.0 to 1.0, where:
            - 0.0 = extremely negative
            - 0.5 = neutral
            - 1.0 = extremely positive
    
    Algorithm:
    ----------
    1. Count occurrences of each sentiment type
    2. Calculate net sentiment: (positive - negative) / total
    3. Classify as positive/negative/neutral based on thresholds:
       - > 0.3: positive (more than 30% net positive)
       - < -0.3: negative (more than 30% net negative)
       - else: neutral (roughly balanced)
    4. Normalize score from [-1, 1] range to [0, 1] range
    
    Thresholds Rationale:
    ---------------------
    - 0.3 threshold prevents small imbalances from being classified as positive/negative
    - Requires significant majority (e.g., 4 positive, 1 negative) to be "positive"
    - This conservative approach reduces false signals
    
    Edge Cases:
    -----------
    - Empty news_items list: Returns ('neutral', 0.5)
    - All neutral articles: Returns ('neutral', 0.5)
    """
    # Initialize counter for each sentiment type
    sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    # Count sentiment occurrences across all news items
    for item in news_items:
        # Get sentiment value, default to 'neutral' if missing
        sentiment = item.get('sentiment', 'neutral')
        sentiments[sentiment] += 1
    
    # Get total number of articles
    total = len(news_items)
    
    # Handle edge case: no articles provided
    if total == 0:
        return 'neutral', 0.5  # Default neutral response
    
    # Calculate sentiment score on scale of -1 to 1
    # Formula: (positives - negatives) / total articles
    # Examples:
    #   - 5 positive, 0 negative, 0 neutral → (5-0)/5 = 1.0 (very positive)
    #   - 2 positive, 3 negative, 0 neutral → (2-3)/5 = -0.2 (slightly negative)
    #   - 1 positive, 1 negative, 3 neutral → (1-1)/5 = 0.0 (neutral)
    score = (sentiments['positive'] - sentiments['negative']) / total
    
    # Classify overall sentiment using threshold-based logic
    if score > 0.3:
        # Strongly positive: more than 30% net positive
        overall = 'positive'
    elif score < -0.3:
        # Strongly negative: more than 30% net negative
        overall = 'negative'
    else:
        # Neutral: balanced or small imbalance
        overall = 'neutral'
    
    # Normalize score from [-1, 1] to [0, 1] for consistency
    # Formula: (score + 1) / 2
    # -1 becomes 0, 0 becomes 0.5, 1 becomes 1
    normalized_score = (score + 1) / 2
    
    return overall, normalized_score

def build_prediction_analysis(query, market, news_items):
    """
    Build a comprehensive AI-powered prediction analysis report.
    
    This is the core analytical function that synthesizes data from multiple sources
    (market odds, trading volume, news sentiment) into a human-readable report that
    explains WHY the current prediction odds are what they are.
    
    Parameters:
    -----------
    query : str
        The user's original search query/topic
    market : dict
        Market data dictionary containing:
        - question: The prediction question
        - yes_price: Current YES probability (0-1)
        - no_price: Current NO probability (0-1)
        - volume: Trading volume
        - liquidity: Available liquidity
        - url: Link to market
    news_items : list of dict
        List of news articles with sentiment labels
    
    Returns:
    --------
    str
        A beautifully formatted multi-line string report containing:
        - Market question and context
        - Current odds visualization
        - Recent news summary
        - Sentiment analysis
        - AI reasoning explaining the odds
        - Confidence assessment
        - Key factors to watch
        - Bottom line recommendation
    
    Report Structure:
    -----------------
    1. Header with query topic
    2. Market question being analyzed
    3. Visual odds display with progress bars
    4. AI research summary section
    5. Recent developments (top 5 news items)
    6. Overall sentiment analysis
    7. AI reasoning (why these odds make sense)
    8. Confidence level assessment
    9. Key factors that could change the prediction
    10. Bottom line conclusion
    
    Design Philosophy:
    ------------------
    This function transforms raw data into narrative reasoning. Instead of just
    showing numbers, it explains the "why" behind predictions, making complex
    prediction markets accessible to non-experts.
    """
    
    # Extract key market data for easy reference
    question = market['question']              # The prediction question
    yes_pct = int(market['yes_price'] * 100)   # Convert 0.55 → 55%
    no_pct = int(market['no_price'] * 100)     # Convert 0.45 → 45%
    
    # Run sentiment analysis on news to understand narrative direction
    overall_sentiment, sentiment_score = analyze_sentiment(news_items)
    
    # ========================================================================
    # BUILD THE FORMATTED ANALYSIS REPORT
    # ========================================================================
    # This section constructs a multi-section report using f-string formatting
    # with Unicode box-drawing characters for visual appeal
    
    # Start building the analysis string with header
    analysis = f"""
╔═══════════════════════════════════════════════════════════════════╗
║  AI PREDICTION ANALYSIS: {query.upper()}                         
╚═══════════════════════════════════════════════════════════════════╝

🎯 MARKET QUESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{question}

📊 CURRENT PREDICTION ODDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   YES: {yes_pct}%  {'█' * int(yes_pct/2)}
   NO:  {no_pct}%   {'█' * int(no_pct/2)}

   Trading Volume: ${float(market['volume']):,.0f}
   Market Liquidity: ${float(market['liquidity']):,.0f}

🔍 AI RESEARCH SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I analyzed {len(news_items)} recent news sources to understand the 
factors driving these odds. Here's what I found:

📰 RECENT DEVELOPMENTS ({len(news_items)} sources analyzed)
"""
    
    # ========================================================================
    # ADD NEWS ITEMS TO REPORT (Top 5 most recent)
    # ========================================================================
    # Loop through news items and format each with emoji indicators
    for i, item in enumerate(news_items[:5], 1):
        # Map sentiment to visual emoji for quick scanning
        # These emojis help users instantly see if news is positive/negative
        sentiment_emoji = {
            'positive': '📈',  # Green chart = good news
            'negative': '📉',  # Red chart = bad news
            'neutral': '➖'    # Horizontal line = neutral news
        }.get(item['sentiment'], '➖')  # Default to neutral if unknown
        
        # Append formatted news item to analysis
        # Truncate summary to 80 chars to keep output compact
        analysis += f"""
   {i}. {sentiment_emoji} {item['title']}
      Source: {item['source']} | Date: {item['date']}
      → {item['summary'][:80]}...
"""
    
    # ========================================================================
    # SENTIMENT ANALYSIS SECTION
    # ========================================================================
    # Add aggregate sentiment findings to help explain market direction
    analysis += f"""

📈 SENTIMENT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall News Sentiment: {overall_sentiment.upper()}
Sentiment Score: {sentiment_score:.2f} ({int(sentiment_score * 100)}%)

Recent news is {'supporting the YES outcome' if sentiment_score > 0.5 else 'supporting the NO outcome' if sentiment_score < 0.5 else 'neutral regarding the outcome'}.

🤖 AI REASONING: Why {yes_pct}% YES?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The current odds of {yes_pct}% reflect:

1. MARKET CONSENSUS
   • Thousands of traders have aggregated information
   • High trading volume (${float(market['volume']):,.0f}) validates these odds
   • Large liquidity suggests strong market confidence

2. NEWS SENTIMENT
   • Recent news is {overall_sentiment}
   • {len([n for n in news_items if n['sentiment'] == 'positive'])} positive signals
   • {len([n for n in news_items if n['sentiment'] == 'negative'])} negative signals
   • {len([n for n in news_items if n['sentiment'] == 'neutral'])} neutral signals

3. CONFIDENCE LEVEL
"""
    
    # ========================================================================
    # CONFIDENCE ASSESSMENT LOGIC
    # ========================================================================
    # Calculate how "sure" the market is based on the spread between YES/NO
    # Larger spread = more confidence, smaller spread = more uncertainty
    
    confidence_spread = abs(yes_pct - no_pct)  # Calculate distance between odds
    
    # Classify confidence using tiered thresholds
    # These thresholds are based on prediction market analysis best practices
    
    if confidence_spread > 30:
        # 70/30 or more extreme = very confident market
        confidence = "VERY HIGH"
        analysis += f"   • {confidence_spread}% spread indicates strong consensus\n"
        analysis += "   • Market is highly confident in the outcome\n"
        analysis += "   • Low volatility expected\n"
        
    elif confidence_spread > 15:
        # 58/42 to 70/30 = confident but not extreme
        confidence = "HIGH"
        analysis += f"   • {confidence_spread}% spread shows clear preference\n"
        analysis += "   • Moderate certainty in the outcome\n"
        analysis += "   • Some volatility possible\n"
        
    elif confidence_spread > 5:
        # 53/47 to 58/42 = slight lean, still uncertain
        confidence = "MODERATE"
        analysis += f"   • {confidence_spread}% spread suggests slight edge\n"
        analysis += "   • Outcome still uncertain\n"
        analysis += "   • High volatility expected\n"
        
    else:
        # 50/50 to 53/47 = basically a coin flip
        confidence = "LOW"
        analysis += f"   • {confidence_spread}% spread means toss-up\n"
        analysis += "   • Extreme uncertainty\n"
        analysis += "   • Very high volatility expected\n"
    
    # ========================================================================
    # KEY FACTORS SECTION
    # ========================================================================
    # Remind users that predictions can change - markets are dynamic
    analysis += f"""

⚖️  KEY FACTORS THAT COULD CHANGE ODDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Events to watch that could shift the prediction:
   • Breaking news or major announcements
   • Changes in underlying fundamentals
   • Shifts in public opinion or polling data
   • Unexpected external events
   • New information becoming available

💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confidence Level: {confidence}
Current Prediction: {yes_pct}% probability of YES

The market has priced in available information to arrive at these
odds. This represents the collective intelligence of thousands of 
informed traders analyzing real-time data.

{'This is a strong signal.' if confidence in ['VERY HIGH', 'HIGH'] else 'This is a weak signal - outcome uncertain.'}

🔗 View on Polymarket: {market['url']}

╚═══════════════════════════════════════════════════════════════════╝
"""
    
    # Return the complete formatted analysis report
    return analysis

# ============================================================================
# STEP 4: MAIN AI ASSISTANT INTERFACE
# ============================================================================

def ai_research_assistant(user_query, newsapi_key=None):
    """
    Main orchestrator function - coordinates the entire analysis pipeline.
    
    This is the primary entry point for the AI research assistant. It takes
    a user's query and executes all necessary steps to produce a comprehensive
    prediction market analysis.
    
    Parameters:
    -----------
    user_query : str
        The user's topic of interest (e.g., "Trump 2024", "Bitcoin $100k")
    newsapi_key : str or None, optional
        API key for NewsAPI.org (if available)
        If None, uses mock/simulated news data
    
    Returns:
    --------
    dict
        A dictionary containing all analysis components:
        - query: The original user query
        - market: The selected market data dictionary
        - news: List of news items analyzed
        - analysis: The full formatted analysis string
    
    Pipeline Steps:
    ---------------
    1. Search Polymarket for relevant prediction markets
    2. Gather recent news and contextual information
    3. Perform sentiment analysis on news
    4. Build comprehensive AI-powered analysis report
    5. Display results to user
    6. Save analysis to text file for future reference
    
    Error Handling:
    ---------------
    - If Polymarket API fails: Falls back to mock market creation
    - If NewsAPI fails/unavailable: Falls back to simulated news data
    - System is resilient and always produces output
    
    Side Effects:
    -------------
    - Prints progress updates to console
    - Saves analysis to 'ai_prediction_analysis.txt' file
    """
    
    # ========================================================================
    # WELCOME HEADER
    # ========================================================================
    print("\n" + "="*70)
    print("  🤖 AI POLYMARKET RESEARCH ASSISTANT")
    print("="*70)
    print(f"\n📝 Your Query: \"{user_query}\"\n")
    
    # ========================================================================
    # STEP 1: SEARCH FOR RELEVANT MARKETS
    # ========================================================================
    print("🔍 Step 1: Searching Polymarket for relevant markets...")
    markets = search_polymarket_markets(user_query)
    
    # Check if we found any markets via API (but don't create mock yet)
    if markets:
        # Success: Display found markets
        print(f"✓ Found {len(markets)} relevant markets\n")
        # Show top 3 markets with their current odds
        for i, m in enumerate(markets[:3], 1):
            print(f"   {i}. {m['question']} ({int(m['yes_price']*100)}% Yes)")
    else:
        print("⚠️  No markets found via API, will create dynamic analysis...")
    
    # ========================================================================
    # STEP 2: GATHER NEWS AND CONTEXT
    # ========================================================================
    print("\n📰 Step 2: Gathering recent news and context...")
    
    # Try to get real news via NewsAPI if key is provided
    news_items = search_with_newsapi(user_query, newsapi_key)
    
    # Check if NewsAPI was successful
    if not news_items:
        # Fallback: Use simulated news data
        print("⚠️  Using simulated news data for demo...")
        news_items = search_news_simple(user_query)
    else:
        # Success: Using real news
        print(f"✓ Found {len(news_items)} recent articles")
    
    print(f"✓ Analyzed {len(news_items)} information sources\n")
    
    # ========================================================================
    # STEP 2.5: CREATE DYNAMIC MOCK MARKET IF NEEDED
    # ========================================================================
    # Now that we have news data, we can create a dynamic mock market
    # with odds calculated from sentiment analysis!
    if not markets:
        print("🎲 Creating prediction market with dynamic odds based on news sentiment...")
        markets = [create_mock_market(user_query, news_items)]
        print(f"   Calculated odds: {int(markets[0]['yes_price']*100)}% YES / {int(markets[0]['no_price']*100)}% NO")
        print("   (Based on sentiment analysis of news)\n")
    
    # Select the most relevant market (first one) for analysis
    market = markets[0]
    print(f"📊 Analyzing: {market['question']}\n")
    
    # ========================================================================
    # STEP 3: BUILD AI ANALYSIS
    # ========================================================================
    print("🤖 Step 3: AI is analyzing data and building prediction reasoning...")
    analysis = build_prediction_analysis(user_query, market, news_items)
    
    # ========================================================================
    # STEP 4: DISPLAY RESULTS
    # ========================================================================
    print("\n" + analysis)
    
    # ========================================================================
    # STEP 5: SAVE TO FILE
    # ========================================================================
    # Save analysis to text file for record-keeping and sharing
    output_file = 'ai_prediction_analysis.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write metadata header
        f.write(f"Query: {user_query}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n" + analysis)
    
    print(f"\n💾 Full analysis saved to: ai_prediction_analysis.txt")
    print("="*70 + "\n")
    
    # ========================================================================
    # RETURN STRUCTURED RESULTS
    # ========================================================================
    # Return all components for programmatic access if needed
    return {
        'query': user_query,      # Original query
        'market': market,         # Selected market data
        'news': news_items,       # News articles analyzed
        'analysis': analysis      # Full formatted report
    }

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

def interactive_mode():
    """
    Launch an interactive REPL-style chat interface with the AI assistant.
    
    This function creates a continuous loop where users can ask multiple
    prediction market questions without restarting the program. It's ideal
    for exploratory analysis of multiple topics in one session.
    
    Features:
    ---------
    - Continuous query loop (no need to restart program)
    - Example queries to guide users
    - Clean input/output formatting
    - Graceful exit with 'quit' command
    
    User Experience Flow:
    ---------------------
    1. Display welcome message and instructions
    2. Show example queries for inspiration
    3. Prompt user for input
    4. Process query through full analysis pipeline
    5. Display results
    6. Prompt for next query (loop continues)
    7. Exit when user types 'quit', 'exit', or 'q'
    
    Error Handling:
    ---------------
    - Empty input: Silently ignored, re-prompts user
    - All exceptions from ai_research_assistant are propagated
      (function will handle them gracefully)
    
    Side Effects:
    -------------
    - Prints to console
    - Calls ai_research_assistant which creates output files
    - Runs until user manually exits
    """
    # ========================================================================
    # DISPLAY WELCOME MESSAGE AND INSTRUCTIONS
    # ========================================================================
    print("\n" + "="*70)
    print("  🤖 AI POLYMARKET RESEARCH ASSISTANT - INTERACTIVE MODE")
    print("="*70)
    print("\nI can analyze any Polymarket prediction topic!")
    print("Just tell me what you want to research.\n")
    
    # Show example queries to help users get started
    print("Examples:")
    print("  - 'Trump 2024 election'")
    print("  - 'Bitcoin $100k'")
    print("  - 'AI safety regulations'")
    print("\nType 'quit' to exit\n")
    print("="*70 + "\n")
    
    # ========================================================================
    # MAIN INTERACTIVE LOOP
    # ========================================================================
    # Continue indefinitely until user chooses to exit
    while True:
        # Prompt user for input
        # .strip() removes leading/trailing whitespace
        user_query = input("🔮 What prediction topic would you like me to analyze?\n> ").strip()
        
        # Check if user wants to exit
        # Accept multiple exit commands for convenience
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Thanks for using the AI Research Assistant!\n")
            break  # Exit the loop and end function
        
        # Ignore empty input (user just pressed Enter)
        if not user_query:
            continue  # Skip to next iteration, re-prompt
        
        # ====================================================================
        # EXECUTE FULL ANALYSIS PIPELINE
        # ====================================================================
        # Call main assistant function with user's query
        ai_research_assistant(user_query)
        
        # ====================================================================
        # DISPLAY CONTINUATION PROMPT
        # ====================================================================
        # Let user know they can enter another query
        print("\n" + "-"*70)
        print("Ready for another query!")
        print("-"*70 + "\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Program entry point - determines execution mode based on command-line args.
    
    This block only executes when the script is run directly (not imported).
    It provides two modes of operation:
    
    1. Command-Line Mode:
       - Run with arguments: python data.py [query]
       - Example: python data.py Trump 2024 election
       - Executes single query and exits
       - Good for: scripting, automation, quick one-off queries
    
    2. Interactive Mode:
       - Run without arguments: python data.py
       - Opens continuous REPL-style interface
       - Good for: exploration, multiple queries, learning
    
    This design pattern follows Unix philosophy: work as both a tool and
    an interactive application.
    """
    # Import sys module for command-line argument access
    import sys
    
    # ========================================================================
    # DETERMINE EXECUTION MODE
    # ========================================================================
    # sys.argv is a list: [script_name, arg1, arg2, ...]
    # len > 1 means user provided arguments after script name
    
    if len(sys.argv) > 1:
        # ====================================================================
        # COMMAND-LINE MODE
        # ====================================================================
        # User provided query as command-line arguments
        # Example: python data.py Bitcoin $100k
        # sys.argv = ['data.py', 'Bitcoin', '$100k']
        
        # Join all arguments (except script name) into single query string
        # sys.argv[1:] excludes the script name (element 0)
        # " ".join(['Bitcoin', '$100k']) → "Bitcoin $100k"
        query = " ".join(sys.argv[1:])
        
        # Execute single analysis and exit
        ai_research_assistant(query)
    else:
        # ====================================================================
        # INTERACTIVE MODE
        # ====================================================================
        # No arguments provided - launch interactive REPL
        # User can ask multiple queries in one session
        interactive_mode()