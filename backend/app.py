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
    Returns high-quality, relevant results with source reputation indicators.
    """
    all_results = []
    
    print(f"\n🔍 GATHERING DATA")
    print(f"   Original query: '{query}'")
    
    # Enhance query for better search results
    enhanced_query = enhance_query(query)
    if enhanced_query != query:
        print(f"   Enhanced query: '{enhanced_query}'")
    
    # 1. Try NewsAPI first (best quality if available)
    if newsapi_client:
        print("\n  📰 NewsAPI:")
        newsapi_results = fetch_newsapi_articles(enhanced_query)
        
        # Add source quality metadata
        for result in newsapi_results:
            source_name = result.get('source', 'Unknown')
            tier = get_source_tier(source_name)
            result['source_tier'] = tier
            result['reputation_badge'] = get_source_reputation_badge(source_name)
            result['quality_score'] = calculate_quality_score(
                source_name, 
                result.get('relevance', 5)
            )
        
        # Filter blacklisted
        newsapi_results = [r for r in newsapi_results if not is_blacklisted(r.get('url', ''))]
        
        # Sort by quality
        newsapi_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        all_results.extend(newsapi_results)
        print(f"     ✓ {len(newsapi_results)} quality articles")
        
        # Show top sources
        for r in newsapi_results[:3]:
            print(f"       • {r.get('source', 'Unknown')} {r.get('reputation_badge', '')}")
    else:
        print("\n  ⚠️  NewsAPI not configured")
        print("     Get free key: https://newsapi.org/")
    
    # 2. Try DuckDuckGo
    print("\n  🦆 DuckDuckGo:")
    ddg_results = scrape_duckduckgo(enhanced_query)
    
    # Add quality scoring
    for result in ddg_results:
        # Filter spam
        if filter_spam_keywords(result.get('title', '') + ' ' + result.get('snippet', '')):
            continue
        
        result['source_tier'] = 4  # Unknown sources
        result['reputation_badge'] = "🌐 Web Result"
        result['quality_score'] = calculate_quality_score('Web Search', 5)
    
    all_results.extend(ddg_results)
    print(f"     ✓ {len(ddg_results)} web results")
    
    # 3. Try MarketWatch for financial queries
    financial_keywords = ['stock', 'market', 'price', 'bitcoin', 'crypto', 'investment', 'trading', 'economy']
    if any(keyword in query.lower() for keyword in financial_keywords):
        print("\n  📈 MarketWatch:")
        marketwatch_results = fetch_marketwatch_news(enhanced_query)
        
        # Add quality metadata
        for result in marketwatch_results:
            result['source_tier'] = 1  # MarketWatch is Tier 1
            result['reputation_badge'] = "🏆 Highly Trusted"
            result['quality_score'] = calculate_quality_score('MarketWatch', 7)
        
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
    
    # Sort by quality score
    unique_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # Take top 10 highest quality results
    final_results = unique_results[:10]
    
    # Summary
    print(f"\n  ✅ QUALITY FILTERED RESULTS: {len(final_results)}")
    
    if final_results:
        tier_counts = {}
        for r in final_results:
            tier = r.get('source_tier', 4)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print(f"     🏆 Tier 1 (Highly Trusted): {tier_counts.get(1, 0)}")
        print(f"     ✅ Tier 2 (Trusted): {tier_counts.get(2, 0)}")
        print(f"     ⚠️  Tier 3 (Verify): {tier_counts.get(3, 0)}")
        print(f"     ❓ Tier 4 (Unknown): {tier_counts.get(4, 0)}")
        
        avg_quality = sum(r.get('quality_score', 0) for r in final_results) / len(final_results)
        print(f"     📊 Average Quality Score: {avg_quality:.1f}/100")
    else:
        print("  ⚠️  No quality results found")
        print("  💡 Try: More specific query or check API keys")
    
    return final_results

def get_prediction_with_confidence(query, web_data):
    """
    Use Claude to analyze the query and web data to provide a prediction with confidence score.
    """
    try:
        # Prepare context from web data
        context = "\n\n".join([
            f"Source {i+1}:\nTitle: {item['title']}\nContent: {item['snippet']}"
            for i, item in enumerate(web_data)
        ])

        prompt = f"""Based on the following web-scraped information from reputable sources, provide a prediction and confidence score for this query:

Query: {query}

Web Data:
{context}

Please analyze this information and provide:
1. A clear prediction or answer to the query
2. A confidence score (0-100) representing how confident you are in this prediction based on the available data
3. Key factors that influenced your confidence score
4. Any important caveats or limitations

Format your response as JSON with the following structure:
{{
    "prediction": "your prediction here",
    "confidence_score": 85,
    "key_factors": ["factor 1", "factor 2"],
    "caveats": ["caveat 1", "caveat 2"]
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse Claude's response
        response_text = message.content[0].text

        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
        except:
            # If JSON parsing fails, create a structured response
            result = {
                "prediction": response_text,
                "confidence_score": 50,
                "key_factors": ["Analysis based on available data"],
                "caveats": ["Unable to parse structured response"]
            }

        return result

    except Exception as e:
        print(f"Error getting prediction: {str(e)}")
        return {
            "prediction": "Unable to generate prediction",
            "confidence_score": 0,
            "key_factors": [],
            "caveats": [f"Error: {str(e)}"]
        }

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main endpoint for predictions - now saves to database!
    """
    try:
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Scrape web data
        web_data = scrape_web_data(query)

        # Get prediction with confidence score from Claude
        result = get_prediction_with_confidence(query, web_data)

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
        except Exception as db_error:
            print(f"Warning: Could not save to database: {db_error}")
            result['saved_to_db'] = False

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})

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
    app.run(debug=True, port=5001, host='127.0.0.1')
