<<<<<<< HEAD
# AI Prediction Tool

An AI-powered prediction tool that uses web-scraped data from reputable sources to provide confidence scores for user queries.

## Tech Stack

- **Frontend**: React with Tailwind CSS
- **Backend**: Python Flask
- **AI**: Claude API (Anthropic)
- **Web Scraping**: BeautifulSoup4 + Requests

## Features

- Real-time web data scraping from reputable sources
- AI-powered prediction analysis using Claude
- Confidence score calculation (0-100)
- Key factors and caveats for each prediction
- Beautiful, responsive UI with Tailwind CSS
- Source attribution for transparency

## Project Structure

```
Claude-Hackathon/
├── backend/
│   ├── app.py              # Flask application with API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── index.js       # React entry point
│   │   └── index.css      # Tailwind CSS imports
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
└── .env                    # Environment variables (API keys)
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Claude API key from Anthropic

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure your `.env` file in the root directory contains your Claude API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

5. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Start both the backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Enter a prediction query (e.g., "Will electric vehicles dominate the market by 2030?")
4. Click "Get Prediction"
5. View the AI-generated prediction with confidence score, key factors, caveats, and sources

## API Endpoints

### POST `/api/predict`
Get a prediction with confidence score for a query.

**Request Body:**
```json
{
  "query": "Your prediction question here"
}
```

**Response:**
```json
{
  "prediction": "The prediction text",
  "confidence_score": 85,
  "key_factors": ["factor 1", "factor 2"],
  "caveats": ["caveat 1", "caveat 2"],
  "sources": [
    {
      "title": "Source title",
      "snippet": "Source content"
    }
  ]
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## How It Works

1. **User Input**: User enters a prediction query through the React frontend
2. **Web Scraping**: Backend scrapes relevant data from web sources using BeautifulSoup
3. **AI Analysis**: Claude API analyzes the scraped data and generates a prediction
4. **Confidence Scoring**: Claude provides a confidence score (0-100) based on data quality and relevance
5. **Results Display**: Frontend displays the prediction, confidence score, key factors, caveats, and sources

## Confidence Score Interpretation

- **80-100**: High confidence (Green)
- **60-79**: Moderate confidence (Yellow)
- **40-59**: Low confidence (Orange)
- **0-39**: Very low confidence (Red)

## Future Enhancements

- Add more reputable data sources
- Implement user authentication
- Save prediction history
- Add export functionality for predictions
- Implement real-time data updates
- Add custom source selection
- Implement rate limiting and caching

## License

MIT
=======
# Claude-Hackathon
>>>>>>> main
