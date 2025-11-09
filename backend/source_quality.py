"""
Source Quality Management
Defines reputable sources and quality scoring for data aggregation.
"""

# Tier 1: Highest quality sources (trusted news organizations)
TIER_1_SOURCES = {
    # US News
    'Reuters', 'Associated Press', 'Bloomberg', 'The Wall Street Journal',
    'The New York Times', 'The Washington Post', 'NPR', 'PBS NewsHour',
    'ProPublica', 'The Atlantic', 'Foreign Policy',
    
    # International News
    'BBC News', 'The Guardian', 'Financial Times', 'The Economist',
    'Al Jazeera English', 'Deutsche Welle', 'France 24',
    
    # Business & Finance
    'CNBC', 'MarketWatch', 'Barron\'s', 'Forbes', 'Fortune',
    'Business Insider', 'Seeking Alpha',
    
    # Tech
    'TechCrunch', 'The Verge', 'Ars Technica', 'Wired',
    
    # Science & Research
    'Nature', 'Science', 'Scientific American', 'MIT Technology Review',
    'The Conversation',
    
    # Fact-Checking
    'PolitiFact', 'FactCheck.org', 'Snopes', 'AP Fact Check'
}

# Tier 2: Good quality sources (established publications)
TIER_2_SOURCES = {
    'USA Today', 'TIME', 'Newsweek', 'Axios', 'Vox', 'Politico',
    'The Hill', 'CBS News', 'NBC News', 'ABC News', 'CNN',
    'Fox News', 'The Independent', 'Daily Mail', 'Express',
    'Yahoo Finance', 'Investopedia', 'CoinDesk', 'CoinTelegraph',
    'ZDNet', 'CNET', 'Engadget', 'Mashable'
}

# Tier 3: Acceptable sources (popular but verify)
TIER_3_SOURCES = {
    'Medium', 'Substack', 'Twitter', 'Reddit', 'Quora',
    'BuzzFeed News', 'HuffPost', 'Slate', 'Salon'
}

# Domains to avoid (known for misinformation or clickbait)
BLACKLISTED_DOMAINS = {
    'example-fake-news.com',  # Add known fake news sites
    'clickbait-site.com',
    # Add more as needed
}

def get_source_tier(source_name):
    """
    Determine the tier/quality level of a source.
    
    Returns:
        1-4: Quality tier (1 is best)
        None: Unknown source
    """
    if not source_name:
        return None
    
    source_lower = source_name.lower()
    
    # Check tier 1
    for tier1 in TIER_1_SOURCES:
        if tier1.lower() in source_lower:
            return 1
    
    # Check tier 2
    for tier2 in TIER_2_SOURCES:
        if tier2.lower() in source_lower:
            return 2
    
    # Check tier 3
    for tier3 in TIER_3_SOURCES:
        if tier3.lower() in source_lower:
            return 3
    
    # Unknown source - lowest tier
    return 4

def is_blacklisted(url):
    """Check if a URL is from a blacklisted domain."""
    if not url:
        return False
    
    url_lower = url.lower()
    for domain in BLACKLISTED_DOMAINS:
        if domain.lower() in url_lower:
            return True
    
    return False

def calculate_quality_score(source_name, relevance_score, recency_days=None):
    """
    Calculate overall quality score for a source.
    
    Parameters:
        source_name: Name of the source
        relevance_score: How relevant the content is (0-10)
        recency_days: How many days old the article is
    
    Returns:
        float: Quality score (0-100)
    """
    # Base score from source tier
    tier = get_source_tier(source_name)
    if tier is None:
        tier_score = 40  # Unknown source gets middle score
    else:
        tier_scores = {1: 100, 2: 80, 3: 60, 4: 40}
        tier_score = tier_scores.get(tier, 40)
    
    # Relevance contribution (0-30 points)
    relevance_contribution = (relevance_score / 10) * 30
    
    # Recency contribution (0-20 points)
    if recency_days is not None:
        if recency_days <= 1:
            recency_contribution = 20
        elif recency_days <= 7:
            recency_contribution = 15
        elif recency_days <= 30:
            recency_contribution = 10
        else:
            recency_contribution = 5
    else:
        recency_contribution = 10  # Default middle score
    
    # Weight the components
    # 50% source reputation, 30% relevance, 20% recency
    final_score = (tier_score * 0.5) + relevance_contribution + recency_contribution
    
    return min(100, max(0, final_score))

def get_source_reputation_badge(source_name):
    """
    Get a reputation indicator for display.
    
    Returns:
        str: Badge emoji/text
    """
    tier = get_source_tier(source_name)
    
    if tier == 1:
        return "🏆 Highly Trusted"
    elif tier == 2:
        return "✅ Trusted"
    elif tier == 3:
        return "⚠️ Verify Claims"
    else:
        return "❓ Unknown Source"

# Query enhancement keywords by topic
TOPIC_KEYWORDS = {
    'election': ['poll', 'vote', 'candidate', 'campaign', 'electoral', 'primary', 'debate'],
    'economy': ['GDP', 'inflation', 'recession', 'employment', 'market', 'stocks', 'bonds'],
    'crypto': ['blockchain', 'bitcoin', 'ethereum', 'cryptocurrency', 'DeFi', 'NFT'],
    'politics': ['policy', 'legislation', 'congress', 'senate', 'government', 'law'],
    'tech': ['AI', 'software', 'hardware', 'innovation', 'startup', 'technology'],
    'climate': ['temperature', 'carbon', 'emissions', 'renewable', 'sustainability'],
    'health': ['disease', 'vaccine', 'treatment', 'medical', 'healthcare', 'pandemic']
}

def enhance_query(query):
    """
    Enhance query with relevant keywords for better search results.
    
    Parameters:
        query: Original search query
    
    Returns:
        str: Enhanced query string
    """
    query_lower = query.lower()
    
    # Detect topic and add relevant keywords
    enhancements = []
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        if topic in query_lower or any(kw.lower() in query_lower for kw in keywords[:2]):
            # Add 2-3 most relevant keywords
            enhancements.extend(keywords[:3])
            break
    
    # Add time-related qualifiers for recent news
    time_keywords = ['latest', 'recent', 'current', 'update', 'news']
    if not any(tk in query_lower for tk in time_keywords):
        enhancements.append('latest')
    
    # Combine original query with enhancements
    if enhancements:
        enhanced = f"{query} {' '.join(enhancements[:3])}"
        return enhanced
    
    return query

def filter_spam_keywords(text):
    """
    Check if text contains spam/clickbait indicators.
    
    Returns:
        bool: True if spam detected
    """
    if not text:
        return False
    
    spam_indicators = [
        'click here', 'you won\'t believe', 'shocking', 'doctors hate',
        'one weird trick', 'make money fast', 'get rich quick',
        'miracle cure', 'lose weight fast', 'secret revealed'
    ]
    
    text_lower = text.lower()
    
    for indicator in spam_indicators:
        if indicator in text_lower:
            return True
    
    return False

