from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
from database import init_db, save_prediction_data, get_recent_queries, get_query_by_id
from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from source_quality import (
    get_source_tier, is_blacklisted, calculate_quality_score,
    get_source_reputation_badge, enhance_query, filter_spam_keywords
)
from data_sources import (
    fetch_google_search, fetch_yahoo_finance,
    fetch_newsapi_articles as fetch_newsapi_enhanced
)

load_dotenv()

app = Flask(__name__)

# Configure CORS with explicit settings
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize database on startup
init_db()

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize NewsAPI client (if key is provided)
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
newsapi_client = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None

def analyze_sentiment(text):
    """
    Analyze sentiment of text using TextBlob.
    Returns 'positive', 'negative', or 'neutral'
    """
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

def fetch_newsapi_articles(query):
    """
    Fetch articles from NewsAPI with better query handling.
    """
    if not newsapi_client:
        print("     ⚠️  NewsAPI not configured (no API key)")
        return []
    
    try:
        # Get articles from last 30 days for better coverage
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Enhance query for better results
        search_query = query
        
        # Search everything
        articles = newsapi_client.get_everything(
            q=search_query,
            from_param=from_date,
            language='en',
            sort_by='relevancy',
            page_size=20  # Get more to filter
        )
        
        results = []
        query_words = set(query.lower().split())
        
        for article in articles.get('articles', []):
            title = article.get('title', '')
            description = article.get('description', '')
            
            # Skip if no title or description
            if not title or not description:
                continue
            
            # Calculate relevance score
            title_lower = title.lower()
            desc_lower = description.lower()
            relevance = sum(1 for word in query_words if word in title_lower or word in desc_lower)
            
            # Only include if reasonably relevant
            if relevance > 0 or len(results) < 2:  # Take some even if low relevance
                text = f"{title} {description}"
                results.append({
                    'title': title,
                    'snippet': description[:200] if description else '',
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
        
        return results[:10]
    except Exception as e:
        print(f"     ❌ NewsAPI error: {str(e)}")
        return []

def fetch_marketwatch_news(query):
    """
    Fetch news from MarketWatch RSS feeds using BeautifulSoup.
    """
    try:
        # MarketWatch RSS feeds
        rss_urls = [
            'https://www.marketwatch.com/rss/topstories',
            'https://www.marketwatch.com/rss/realtimeheadlines',
        ]
        
        results = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for rss_url in rss_urls:
            try:
                response = requests.get(rss_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'xml')
                
                items = soup.find_all('item', limit=10)
                
                for item in items:
                    title_elem = item.find('title')
                    description_elem = item.find('description')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    description = description_elem.get_text(strip=True) if description_elem else ''
                    
                    # Check if query terms are in title or description
                    if any(word.lower() in title.lower() or word.lower() in description.lower() 
                           for word in query.split()):
                        text = f"{title} {description}"
                        results.append({
                            'title': title,
                            'snippet': description[:200] if description else '',
                            'source': 'MarketWatch',
                            'url': link_elem.get_text(strip=True) if link_elem else '',
                            'sentiment': analyze_sentiment(text),
                            'published_at': pubdate_elem.get_text(strip=True) if pubdate_elem else ''
                        })
                        
                        if len(results) >= 5:
                            break
            except Exception as e:
                print(f"Error parsing MarketWatch feed {rss_url}: {e}")
                continue
            
            if len(results) >= 5:
                break
        
        return results
    except Exception as e:
        print(f"MarketWatch RSS error: {str(e)}")
        return []

def scrape_duckduckgo(query):
    """
    Scrape web data from DuckDuckGo with relevance filtering.
    """
    try:
        # URL encode the query properly
        from urllib.parse import quote_plus
        encoded_query = quote_plus(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = []
        result_divs = soup.find_all('div', class_='result', limit=15)  # Get more to filter
        
        query_words = set(query.lower().split())

        for div in result_divs:
            title_elem = div.find('a', class_='result__a')
            snippet_elem = div.find('a', class_='result__snippet')

            if title_elem and snippet_elem:
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True)
                
                # Calculate relevance
                title_lower = title.lower()
                snippet_lower = snippet.lower()
                relevance = sum(1 for word in query_words if word in title_lower or word in snippet_lower)
                
                # Only include if relevant
                if relevance > 0:
                    text = f"{title} {snippet}"
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'source': 'Web Search',
                        'sentiment': analyze_sentiment(text),
                        'relevance': relevance
                    })

        # Sort by relevance
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Remove relevance score
        for r in results:
            r.pop('relevance', None)
        
        return results[:10]
    except Exception as e:
        print(f"     ❌ Error scraping DuckDuckGo: {str(e)}")
        return []

def scrape_web_data(query):
    """
    Aggregate data from multiple sources with quality scoring and filtering.
    ACTIVE SOURCES: Google, Yahoo Finance, NewsAPI, MarketWatch (Reddit removed per user request)
    Returns high-quality, relevant results with source reputation indicators.
    """
    all_results = []
    
    print(f"\n🔍 GATHERING DATA FROM ALL SOURCES")
    print(f"   Original query: '{query}'")
    
    # Enhance query for better search results
    enhanced_query = enhance_query(query)
    if enhanced_query != query:
        print(f"   Enhanced query: '{enhanced_query}'")
    
    # 1. Try Google Custom Search API (HIGHEST QUALITY)
    print("\n  🔍 Google Search:")
    google_results = fetch_google_search(enhanced_query, limit=10)
    for result in google_results:
        source_name = result.get('source', 'Unknown')
        tier = get_source_tier(source_name)
        result['source_tier'] = tier
        result['reputation_badge'] = get_source_reputation_badge(source_name)
        result['quality_score'] = calculate_quality_score(source_name, 8)
    all_results.extend(google_results)
    
    # 2. Try NewsAPI (HIGH QUALITY NEWS)
    print("\n  📰 NewsAPI:")
    newsapi_results = fetch_newsapi_enhanced(enhanced_query, limit=10)
    for result in newsapi_results:
        source_name = result.get('source', 'Unknown')
        tier = get_source_tier(source_name)
        result['source_tier'] = tier
        result['reputation_badge'] = get_source_reputation_badge(source_name)
        result['quality_score'] = calculate_quality_score(source_name, 7)
    
    # Filter blacklisted
    newsapi_results = [r for r in newsapi_results if not is_blacklisted(r.get('url', ''))]
    all_results.extend(newsapi_results)
    
    # Show top sources
    if newsapi_results:
        for r in newsapi_results[:3]:
            print(f"       • {r.get('source', 'Unknown')} {r.get('reputation_badge', '')}")
    
    # 3. Try Yahoo Finance (FINANCIAL DATA)
    financial_keywords = ['stock', 'market', 'price', 'bitcoin', 'crypto', 'investment', 'trading', 'economy', '$']
    if any(keyword in query.lower() for keyword in financial_keywords):
        print("\n  💰 Yahoo Finance:")
        yahoo_results = fetch_yahoo_finance(enhanced_query, limit=5)
        for result in yahoo_results:
            result['source_tier'] = 1  # Yahoo Finance is Tier 1
            result['reputation_badge'] = "📊 Financial Data"
            result['quality_score'] = calculate_quality_score('Yahoo Finance', 8)
        all_results.extend(yahoo_results)
    
    # 4. Try MarketWatch for financial queries
    if any(keyword in query.lower() for keyword in financial_keywords):
        print("\n  📈 MarketWatch:")
        marketwatch_results = fetch_marketwatch_news(enhanced_query)
        for result in marketwatch_results:
            result['source_tier'] = 1  # MarketWatch is Tier 1
            result['reputation_badge'] = "🏆 Highly Trusted"
            result['quality_score'] = calculate_quality_score('MarketWatch', 8)
        all_results.extend(marketwatch_results)
        print(f"     ✓ {len(marketwatch_results)} financial articles")
    
    # Remove duplicates and filter
    seen_titles = set()
    unique_results = []
    
    for result in all_results:
        title = result.get('title', '').lower().strip()
        
        # Skip if duplicate, too short, or spam
        if not title or len(title) < 15:
            continue
        if title in seen_titles:
            continue
        if filter_spam_keywords(title):
            print(f"     ⚠️  Filtered spam: {title[:50]}...")
            continue
        
        seen_titles.add(title)
        unique_results.append(result)
    
    # Calculate relevance score for each result
    query_words = set(query.lower().split())
    for result in unique_results:
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Calculate word overlap
        title_words = set(title.split())
        snippet_words = set(snippet.split())
        
        # Relevance = number of query words found
        relevance = len(query_words & (title_words | snippet_words))
        
        # Boost if query words appear in title (more important)
        title_relevance = len(query_words & title_words) * 2
        
        # Combined relevance score (0-100)
        max_possible = len(query_words) * 3  # title words count 2x + snippet 1x
        relevance_score = ((relevance + title_relevance) / max(max_possible, 1)) * 100
        
        result['relevance_score'] = min(relevance_score, 100)
        
        # Combine quality and relevance for final score
        # 60% quality, 40% relevance
        result['final_score'] = (
            result.get('quality_score', 0) * 0.6 + 
            result.get('relevance_score', 0) * 0.4
        )
    
    # Sort by combined score (quality + relevance)
    unique_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
    
    # Take top 12 most relevant and high-quality results
    final_results = unique_results[:12]
    
    # Log relevance info
    if final_results:
        avg_relevance = sum(r.get('relevance_score', 0) for r in final_results) / len(final_results)
        print(f"     🎯 Average Relevance Score: {avg_relevance:.1f}/100")
    
    # Summary
    print(f"\n  ✅ QUALITY FILTERED RESULTS: {len(final_results)}")
    
    if final_results:
        tier_counts = {}
        source_counts = {}
        for r in final_results:
            tier = r.get('source_tier', 4)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            # Count sources
            source = r.get('source', 'Unknown')
            if 'reddit' in source.lower():
                source_counts['Reddit'] = source_counts.get('Reddit', 0) + 1
            elif 'google' in source.lower() or r.get('quality_score', 0) >= 80:
                source_counts['Google'] = source_counts.get('Google', 0) + 1
            elif 'yahoo' in source.lower():
                source_counts['Yahoo Finance'] = source_counts.get('Yahoo Finance', 0) + 1
            elif 'marketwatch' in source.lower():
                source_counts['MarketWatch'] = source_counts.get('MarketWatch', 0) + 1
            else:
                source_counts['News/Web'] = source_counts.get('News/Web', 0) + 1
        
        print(f"\n  📊 SOURCE BREAKDOWN:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"     • {source}: {count}")
        
        print(f"\n  🏅 QUALITY TIERS:")
        print(f"     🏆 Tier 1 (Highly Trusted): {tier_counts.get(1, 0)}")
        print(f"     ✅ Tier 2 (Trusted): {tier_counts.get(2, 0)}")
        print(f"     ⚠️  Tier 3 (Community): {tier_counts.get(3, 0)}")
        print(f"     ❓ Tier 4 (Unknown): {tier_counts.get(4, 0)}")
        
        avg_quality = sum(r.get('quality_score', 0) for r in final_results) / len(final_results)
        print(f"     📈 Average Quality Score: {avg_quality:.1f}/100")
    else:
        print("  ⚠️  No quality results found")
        print("  💡 Try: More specific query or check API keys")
    
    return final_results

def calculate_data_driven_confidence(web_data):
    """
    Calculate a base confidence score based on the quality and diversity of retrieved data.
    This provides an OBJECTIVE scoring component that works with Claude AI's subjective analysis.
    
    HYBRID CONFIDENCE SYSTEM:
    - This function: Objective data quality metrics (0-30 points)
    - Claude AI: Subjective evidence analysis (0-40 points)
    - Final Score = 40 (base) + Data Quality + AI Analysis
    
    Returns: dict with confidence_boost (0-30), analysis breakdown
    """
    if not web_data:
        return {'confidence_boost': 0, 'reason': 'No data retrieved'}
    
    # Count sources by platform (Reddit removed per user request)
    platform_counts = {
        'google': 0,
        'newsapi': 0,
        'yahoo_finance': 0,
        'marketwatch': 0
    }
    
    total_quality = 0
    total_relevance = 0
    source_count = len(web_data)
    
    for item in web_data:
        source = item.get('source', '').lower()
        
        # Categorize by platform (Reddit removed)
        if 'yahoo finance' in source or 'finance.yahoo' in item.get('url', ''):
            platform_counts['yahoo_finance'] += 1
        elif 'marketwatch' in source:
            platform_counts['marketwatch'] += 1
        elif item.get('from_newsapi'):
            platform_counts['newsapi'] += 1
        else:
            platform_counts['google'] += 1
        
        # Accumulate quality and relevance
        total_quality += item.get('quality_score', 50)
        total_relevance += item.get('relevance_score', 50)
    
    # Calculate metrics
    avg_quality = total_quality / source_count if source_count > 0 else 0
    avg_relevance = total_relevance / source_count if source_count > 0 else 0
    platforms_used = sum(1 for count in platform_counts.values() if count > 0)
    
    # CONFIDENCE BOOST CALCULATION (0-30 points)
    confidence_boost = 0
    reasons = []
    
    # 1. Source Quantity (0-10 points)
    if source_count >= 10:
        confidence_boost += 10
        reasons.append(f"✓ Excellent data: {source_count} sources")
    elif source_count >= 7:
        confidence_boost += 7
        reasons.append(f"✓ Good data: {source_count} sources")
    elif source_count >= 4:
        confidence_boost += 4
        reasons.append(f"○ Moderate data: {source_count} sources")
    else:
        confidence_boost += 2
        reasons.append(f"⚠ Limited data: {source_count} sources")
    
    # 2. Platform Diversity (0-10 points) - Max 4 platforms (Google, NewsAPI, Yahoo Finance, MarketWatch)
    if platforms_used >= 4:
        confidence_boost += 10
        reasons.append(f"✓ Excellent diversity: {platforms_used}/4 platforms")
    elif platforms_used >= 3:
        confidence_boost += 7
        reasons.append(f"✓ Good diversity: {platforms_used}/4 platforms")
    elif platforms_used >= 2:
        confidence_boost += 5
        reasons.append(f"○ Moderate diversity: {platforms_used}/4 platforms")
    else:
        confidence_boost += 2
        reasons.append(f"⚠ Low diversity: {platforms_used}/4 platform")
    
    # 3. Average Quality (0-10 points)
    if avg_quality >= 80:
        confidence_boost += 10
        reasons.append(f"✓ High quality sources: {avg_quality:.0f}/100")
    elif avg_quality >= 65:
        confidence_boost += 7
        reasons.append(f"✓ Good quality sources: {avg_quality:.0f}/100")
    elif avg_quality >= 50:
        confidence_boost += 4
        reasons.append(f"○ Moderate quality sources: {avg_quality:.0f}/100")
    else:
        confidence_boost += 2
        reasons.append(f"⚠ Lower quality sources: {avg_quality:.0f}/100")
    
    # Platform breakdown for display
    platform_details = []
    for platform, count in platform_counts.items():
        if count > 0:
            platform_name = platform.replace('_', ' ').title()
            platform_details.append(f"{platform_name}: {count}")
    
    return {
        'confidence_boost': confidence_boost,
        'reasons': reasons,
        'platform_details': platform_details,
        'avg_quality': avg_quality,
        'avg_relevance': avg_relevance,
        'platforms_used': platforms_used,
        'source_count': source_count
    }

def get_prediction_with_confidence(query, web_data):
    """
    Use Claude to analyze the query and web data to provide a DEFINITIVE prediction with confidence score.
    Enhanced for: Better source relevance, more decisive predictions, DATA-DRIVEN confidence scoring.
    """
    try:
        # Calculate data-driven confidence metrics
        data_metrics = calculate_data_driven_confidence(web_data)
        
        print(f"\n📊 DATA QUALITY ANALYSIS:")
        for reason in data_metrics['reasons']:
            print(f"   {reason}")
        print(f"   Platforms: {', '.join(data_metrics['platform_details'])}")
        print(f"   Base Confidence Boost: +{data_metrics['confidence_boost']} points")
        
        # Limit to top 10 sources to prevent context overflow
        limited_data = web_data[:10]
        
        # Prepare context from web data with quality indicators
        context_parts = []
        for i, item in enumerate(limited_data):
            quality_badge = item.get('reputation_badge', '')
            source_name = item.get('source', 'Unknown')
            # Truncate snippet to 200 chars to prevent too long context
            snippet = item.get('snippet', '')[:200]
            context_parts.append(
                f"Source {i+1} [{quality_badge} - {source_name}]:\n"
                f"Title: {item.get('title', 'No title')}\n"
                f"Content: {snippet}\n"
                f"Quality: {item.get('quality_score', 0)}/100"
            )
        context = "\n\n".join(context_parts)
        
        # Ensure context isn't too long
        if len(context) > 8000:
            context = context[:8000] + "\n...[truncated for length]"

        prompt = f"""You are a DEFINITIVE prediction analyst who MUST take a clear stance. NO WAVERING ALLOWED.

Query: {query}

High-Quality Web Data (sorted by relevance and trustworthiness):
{context}

📊 DATA QUALITY METRICS (OBJECTIVE - from scraped web sources):
• Total Sources Scraped: {data_metrics['source_count']}
• Platforms Used: {data_metrics['platforms_used']}/4 ({', '.join(data_metrics['platform_details'])})
• Average Source Quality: {data_metrics['avg_quality']:.0f}/100
• Average Relevance: {data_metrics['avg_relevance']:.0f}/100
• Objective Data Quality Boost: +{data_metrics['confidence_boost']} points

⚙️ HYBRID CONFIDENCE SYSTEM:
Your confidence score combines TWO components:
1. OBJECTIVE: Scraped data quality (+{data_metrics['confidence_boost']} points already calculated)
2. SUBJECTIVE: Your AI analysis of evidence strength (you add 0-40 points based on content)

Final Score = 40 (base) + {data_metrics['confidence_boost']} (data quality) + YOUR analysis (0-40)

ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:

1. **TAKE A STANCE**: You MUST pick ONE side. NO "maybe", "might", "could", "possibly", or "it depends"
2. **START WITH YOUR ANSWER**: Begin with EXACTLY one of these:
   - "YES" - if you believe it WILL happen
   - "NO" - if you believe it WILL NOT happen
   - "HIGHLY LIKELY" - if strong evidence supports it happening
   - "UNLIKELY" - if evidence suggests it won't happen
3. **COMMIT TO YOUR POSITION**: After stating Yes/No, defend that position with conviction
4. **NO FENCE-SITTING**: Don't say "on one hand... on the other hand". Pick the stronger side and argue for it
5. **USE DECISIVE LANGUAGE**: "will happen", "will reach", "will dominate" NOT "may happen", "could reach", "might dominate"

BANNED WORDS/PHRASES (Do NOT use these):
- "may", "might", "could", "possibly", "potentially", "perhaps"
- "it depends", "it's unclear", "both sides", "mixed signals"
- "on the other hand", "however it's possible", "but also"

Format your response as JSON:
{{
    "prediction": "START WITH YES/NO/HIGHLY LIKELY/UNLIKELY, then provide strong reasoning for YOUR definitive stance. No wavering between options.",
    "confidence_score": 85,
    "key_factors": ["ONLY evidence supporting YOUR chosen stance", "Data that backs YOUR position", "Why YOUR answer is correct"],
    "caveats": ["What could prove YOUR prediction wrong", "Limitations of YOUR stance"]
}}

**CONFIDENCE SCORING GUIDELINES** (HYBRID: Scraped Data + AI Analysis):

Your confidence score MUST reflect BOTH components of the hybrid system:

COMPONENT 1 - OBJECTIVE (Already done):
Base: 40 + Data Quality: {data_metrics['confidence_boost']} = {40 + data_metrics['confidence_boost']}% 
This is calculated from scraped sources (Google, NewsAPI, Yahoo Finance, MarketWatch)

COMPONENT 2 - SUBJECTIVE (Your task):
Analyze the CONTENT of the sources and add 0-40 points based on evidence strength:
   - Strong supporting evidence for your stance: +30 to +40 points → Final: 85-100%
   - Clear trend supporting your stance: +20 to +30 points → Final: 70-84%
   - Moderate evidence, slight lean: +10 to +20 points → Final: 55-69%
   - Weak evidence, minimal lean: +0 to +10 points → Final: 40-54%
   - Contradictory/unclear evidence: -5 to 0 points → Final: 35-45%

REAL EXAMPLES (showing BOTH components):
- 10 sources, 4 platforms, quality 78 (Data: +27) + strong bullish trend (AI: +35) = 40+27+35 = 102% → cap at 100%
- 7 sources, 3 platforms, quality 72 (Data: +21) + clear upward trend (AI: +25) = 40+21+25 = 86%
- 5 sources, 2 platforms, quality 65 (Data: +14) + moderate positive (AI: +15) = 40+14+15 = 69%
- 3 sources, 1 platform, quality 55 (Data: +6) + weak evidence (AI: +5) = 40+6+5 = 51%

**CRITICAL**: The confidence score is influenced by BOTH scraped data quality AND your AI content analysis!

REMEMBER: Pick a side and defend it. Users need CLEAR answers, not diplomatic hedging. Even if evidence is mixed, analyze which side is STRONGER and commit to that position. BE BOLD and reasonably confident."""

        # Call Claude API with timeout protection
        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                timeout=60.0,  # 60 second timeout
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as api_error:
            print(f"❌ Claude API call failed: {str(api_error)}")
            raise Exception(f"Claude API error: {str(api_error)}")

        # Parse Claude's response
        try:
            response_text = message.content[0].text
            print(f"📝 Claude response length: {len(response_text)} chars")
        except (IndexError, AttributeError) as parse_error:
            print(f"❌ Failed to extract Claude response: {parse_error}")
            raise Exception("Invalid response format from Claude")

        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                print("⚠️  No JSON found in response, using raw text")
                result = {
                    "prediction": response_text,
                    "confidence_score": 50,
                    "key_factors": ["Analysis based on available data"],
                    "caveats": ["Response not in expected JSON format"]
                }
            else:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                print(f"✓ Successfully parsed JSON response")
                
        except json.JSONDecodeError as json_error:
            print(f"⚠️  JSON parsing failed: {json_error}")
            # If JSON parsing fails, create a structured response
            result = {
                "prediction": response_text,
                "confidence_score": 50,
                "key_factors": ["Analysis based on available data"],
                "caveats": ["Response format could not be parsed"]
            }

        # Add data quality metrics to the result
        result['data_quality'] = {
            'source_count': data_metrics['source_count'],
            'platforms_used': data_metrics['platforms_used'],
            'platform_breakdown': data_metrics['platform_details'],
            'avg_quality_score': round(data_metrics['avg_quality'], 1),
            'avg_relevance_score': round(data_metrics['avg_relevance'], 1),
            'confidence_boost': data_metrics['confidence_boost']
        }

        return result

    except Exception as e:
        print(f"❌ Error in get_prediction_with_confidence: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "prediction": "Unable to generate prediction due to an error",
            "confidence_score": 0,
            "key_factors": ["Error occurred during analysis"],
            "caveats": [f"Technical error: {str(e)}"]
        }

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """
    Main endpoint for predictions - now saves to database!
    Enhanced with better error handling and logging.
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        print(f"\n🚀 Processing prediction request for: '{query}'")

        # Scrape web data with error handling
        try:
            web_data = scrape_web_data(query)
            print(f"✓ Collected {len(web_data)} data sources")
        except Exception as scrape_error:
            print(f"❌ Error scraping data: {scrape_error}")
            return jsonify({'error': f'Failed to gather data: {str(scrape_error)}'}), 500

        if not web_data or len(web_data) == 0:
            return jsonify({
                'error': 'No data sources found for this query. Please try a different query or check API keys.',
                'suggestion': 'Try being more specific or use different keywords'
            }), 404

        # Get prediction with confidence score from Claude
        try:
            print(f"🤖 Generating prediction with Claude...")
            result = get_prediction_with_confidence(query, web_data)
            print(f"✓ Prediction generated: {result.get('confidence_score', 0)}% confidence")
        except Exception as claude_error:
            print(f"❌ Error from Claude API: {claude_error}")
            return jsonify({
                'error': 'Failed to generate prediction',
                'details': str(claude_error)
            }), 500

        # Add web sources to response
        result['sources'] = web_data

        # Save to database
        try:
            db_result = save_prediction_data(
                query_text=query,
                prediction_text=result.get('prediction', ''),
                confidence_score=result.get('confidence_score', 0),
                key_factors=result.get('key_factors', []),
                caveats=result.get('caveats', []),
                sources=web_data,
                model_used="claude-sonnet-4-5-20250929"
            )
            result['saved_to_db'] = db_result.get('success', False)
            result['query_id'] = db_result.get('query_id')
            print(f"✓ Saved to database (ID: {result.get('query_id')})")
        except Exception as db_error:
            print(f"⚠️  Could not save to database: {db_error}")
            result['saved_to_db'] = False

        print(f"✅ Request completed successfully\n")
        return jsonify(result)

    except Exception as e:
        print(f"❌ Unexpected error in predict endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})

@app.route('/favicon.ico')
def favicon():
    """
    Favicon endpoint - returns 204 No Content
    """
    return '', 204

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors
    """
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            'POST /api/predict - Make a prediction',
            'GET /api/health - Health check',
            'GET /api/history - Get prediction history',
            'GET /api/stats - Get statistics'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """
    Handle 405 Method Not Allowed errors
    """
    return jsonify({
        'error': 'Method not allowed',
        'message': f'The {request.method} method is not allowed for this endpoint',
        'hint': 'Use POST for /api/predict endpoint'
    }), 405

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get recent prediction history.
    Query params:
      - limit: Number of records to return (default: 10, max: 50)
    """
    try:
        limit = int(request.args.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50 records
        
        queries = get_recent_queries(limit=limit)
        
        return jsonify({
            'count': len(queries),
            'queries': queries
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/<int:query_id>', methods=['GET'])
def get_query(query_id):
    """
    Get a specific query by ID with all related data.
    """
    try:
        query_data = get_query_by_id(query_id)
        
        if not query_data:
            return jsonify({'error': 'Query not found'}), 404
        
        return jsonify(query_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Get database statistics.
    """
    try:
        from database import SessionLocal, Query, Prediction, Source
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            total_queries = db.query(func.count(Query.id)).scalar()
            total_predictions = db.query(func.count(Prediction.id)).scalar()
            total_sources = db.query(func.count(Source.id)).scalar()
            
            # Get average confidence score
            avg_confidence = db.query(func.avg(Prediction.confidence_score)).scalar()
            avg_confidence = round(avg_confidence, 2) if avg_confidence else 0
            
            return jsonify({
                'total_queries': total_queries,
                'total_predictions': total_predictions,
                'total_sources': total_sources,
                'average_confidence_score': avg_confidence
            })
        finally:
            db.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/sources', methods=['POST'])
def debug_sources():
    """
    Debug endpoint to see what sources are being found for a query.
    Returns detailed information about source quality and relevance.
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get sources with all metadata
        sources = scrape_web_data(query)
        
        # Format for debugging
        debug_info = {
            'original_query': query,
            'enhanced_query': enhance_query(query),
            'total_sources_found': len(sources),
            'sources': []
        }
        
        for source in sources:
            debug_info['sources'].append({
                'title': source.get('title'),
                'source': source.get('source'),
                'reputation_badge': source.get('reputation_badge'),
                'source_tier': source.get('source_tier'),
                'quality_score': source.get('quality_score'),
                'sentiment': source.get('sentiment'),
                'snippet': source.get('snippet', '')[:100] + '...',
                'url': source.get('url')
            })
        
        return jsonify(debug_info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use PORT environment variable for production (Render, Heroku, etc.)
    # Default to 5001 for local development
    port = int(os.environ.get('PORT', 5001))
    # Use debug=True for local, False for production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    # Use 0.0.0.0 for production (allows external connections)
    # Use 127.0.0.1 for local (localhost only)
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    
    app.run(debug=debug_mode, port=port, host=host)
