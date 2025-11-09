import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5001/api/predict', {
        query: query
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while fetching the prediction');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getConfidenceBarColor = (score) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-800 mb-4">
              AI Prediction Tool
            </h1>
            <p className="text-xl text-gray-600">
              Get confident predictions based on real-time web data
            </p>
          </div>

          {/* Search Form */}
          <div className="bg-white rounded-lg shadow-xl p-8 mb-8">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label htmlFor="query" className="block text-gray-700 text-lg font-semibold mb-3">
                  What would you like to predict?
                </label>
                <input
                  type="text"
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., Will electric vehicles dominate the market by 2030?"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed text-lg"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </span>
                ) : (
                  'Get Prediction'
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8">
              <p className="font-semibold">Error:</p>
              <p>{error}</p>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="bg-white rounded-lg shadow-xl p-8 space-y-6">
              {/* Confidence Score */}
              <div className="border-b pb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Confidence Score</h2>
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-6">
                      <div
                        className={`h-6 rounded-full ${getConfidenceBarColor(result.confidence_score)} transition-all duration-500`}
                        style={{ width: `${result.confidence_score}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className={`text-4xl font-bold ${getConfidenceColor(result.confidence_score)}`}>
                    {result.confidence_score}%
                  </div>
                </div>
              </div>

              {/* Prediction */}
              <div className="border-b pb-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">Prediction</h2>
                <p className="text-gray-700 text-lg leading-relaxed">{result.prediction}</p>
              </div>

              {/* Key Factors */}
              {result.key_factors && result.key_factors.length > 0 && (
                <div className="border-b pb-6">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Key Factors</h2>
                  <ul className="space-y-2">
                    {result.key_factors.map((factor, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2 mt-1">•</span>
                        <span className="text-gray-700">{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Caveats */}
              {result.caveats && result.caveats.length > 0 && (
                <div className="border-b pb-6">
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Important Caveats</h2>
                  <ul className="space-y-2">
                    {result.caveats.map((caveat, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-yellow-600 mr-2 mt-1">⚠</span>
                        <span className="text-gray-700">{caveat}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Sources */}
              {result.sources && result.sources.length > 0 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Sources</h2>
                  <div className="space-y-3">
                    {result.sources.map((source, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-gray-800 mb-2">{source.title}</h3>
                        <p className="text-gray-600 text-sm">{source.snippet}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
