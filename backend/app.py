from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def scrape_web_data(query):
    """
    Scrape web data from reputable sources based on the query.
    This is a basic implementation - you can expand this to scrape specific sources.
    """
    try:
        # Using DuckDuckGo HTML for basic web search (no API key needed)
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract search results
        results = []
        result_divs = soup.find_all('div', class_='result', limit=5)

        for div in result_divs:
            title_elem = div.find('a', class_='result__a')
            snippet_elem = div.find('a', class_='result__snippet')

            if title_elem and snippet_elem:
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'snippet': snippet_elem.get_text(strip=True)
                })

        return results
    except Exception as e:
        print(f"Error scraping web data: {str(e)}")
        return []

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
    Main endpoint for predictions
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

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
