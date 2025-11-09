import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);

  useEffect(() => {
    if (result) {
      setTimeout(() => setShowResult(true), 100);
    }
  }, [result]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setShowResult(false);

    try {
      // Use deployed backend URL from environment variable, fallback to localhost for development
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      const response = await axios.post(`${API_URL}/api/predict`, {
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
    if (score >= 85) return 'from-emerald-500 to-green-600';
    if (score >= 70) return 'from-green-500 to-emerald-500';
    if (score >= 55) return 'from-blue-500 to-cyan-500';
    if (score >= 40) return 'from-amber-500 to-yellow-600';
    return 'from-orange-500 to-red-500';
  };

  const getConfidenceBadge = (score) => {
    if (score >= 85) return { text: 'Very High Confidence', color: 'bg-emerald-100 text-emerald-800 border-emerald-300' };
    if (score >= 70) return { text: 'High Confidence', color: 'bg-green-100 text-green-800 border-green-300' };
    if (score >= 55) return { text: 'Moderate Confidence', color: 'bg-blue-100 text-blue-800 border-blue-300' };
    if (score >= 40) return { text: 'Low Confidence', color: 'bg-amber-100 text-amber-800 border-amber-300' };
    return { text: 'Very Low Confidence', color: 'bg-orange-100 text-orange-800 border-orange-300' };
  };

  const getOutcomeType = (prediction) => {
    const lower = prediction.toLowerCase();
    // Check for YES answers
    if (lower.startsWith('yes') || lower.startsWith('highly likely')) {
      return { 
        icon: '✓', 
        color: 'text-emerald-600', 
        bg: 'bg-emerald-50',
        label: lower.startsWith('yes') ? 'YES' : 'HIGHLY LIKELY',
        labelColor: 'text-emerald-600'
      };
    }
    // Check for NO answers
    if (lower.startsWith('no') || lower.startsWith('unlikely')) {
      return { 
        icon: '✗', 
        color: 'text-red-600', 
        bg: 'bg-red-50',
        label: lower.startsWith('no') ? 'NO' : 'UNLIKELY',
        labelColor: 'text-red-600'
      };
    }
    // Check for LIKELY (without highly)
    if (lower.startsWith('likely')) {
      return { 
        icon: '↗', 
        color: 'text-blue-600', 
        bg: 'bg-blue-50',
        label: 'LIKELY',
        labelColor: 'text-blue-600'
      };
    }
    // Fallback (shouldn't happen with new prompt)
    return { 
      icon: '?', 
      color: 'text-gray-600', 
      bg: 'bg-gray-50',
      label: 'ANALYZING',
      labelColor: 'text-gray-600'
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute w-96 h-96 -top-48 -left-48 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute w-96 h-96 -bottom-48 -right-48 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute w-96 h-96 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative container mx-auto px-4 py-8 sm:py-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-block mb-6">
              <div className="flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 shadow-2xl shadow-purple-500/50 mx-auto">
                <span className="text-4xl">🔮</span>
              </div>
            </div>
            <h1 className="text-5xl sm:text-7xl font-black bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-blue-500 mb-4 tracking-tight">
              Poly Predictor
            </h1>
            <p className="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto">
              AI-powered predictions backed by premium data sources
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2 mt-4 text-xs sm:text-sm text-gray-400">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Google
              </span>
              <span className="text-gray-600">•</span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                NewsAPI
              </span>
              <span className="text-gray-600">•</span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
                Yahoo Finance
              </span>
              <span className="text-gray-600">•</span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span>
                MarketWatch
              </span>
            </div>
          </div>

          {/* Search Form */}
          <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-10 mb-8 hover:bg-white/15 transition-all duration-300">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="query" className="block text-white text-base sm:text-lg font-semibold mb-3 flex items-center gap-2">
                  <span className="text-2xl">💭</span>
                  What do you want to know?
                </label>
                <input
                  type="text"
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Will electric vehicles dominate by 2030?"
                  className="w-full px-5 sm:px-6 py-4 sm:py-5 bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-500 text-white placeholder-gray-400 text-base sm:text-lg transition-all duration-300"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 sm:py-5 px-8 rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed text-base sm:text-lg shadow-2xl shadow-purple-500/50 hover:shadow-pink-500/50 hover:scale-105 transform"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-3">
                    <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-lg">Analyzing Data...</span>
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2 text-lg">
                    <span>🚀</span>
                    Get Prediction
                  </span>
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="backdrop-blur-xl bg-red-500/20 border-2 border-red-500/50 text-white px-6 py-5 rounded-2xl mb-8 animate-shake">
              <p className="font-bold flex items-center gap-2 mb-2">
                <span className="text-2xl">⚠️</span>
                Error Occurred
              </p>
              <p className="text-red-100">{error}</p>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className={`space-y-6 transform transition-all duration-700 ${showResult ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
              {/* Outcome Card */}
              <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-10">
                {/* Definitive Answer Banner */}
                <div className={`mb-6 p-4 rounded-2xl ${getOutcomeType(result.prediction).bg} border-2 ${getOutcomeType(result.prediction).color.replace('text', 'border')}`}>
                  <div className="flex items-center justify-center gap-4">
                    <span className={`text-5xl ${getOutcomeType(result.prediction).color}`}>
                      {getOutcomeType(result.prediction).icon}
                    </span>
                    <div>
                      <div className="text-xs text-gray-600 font-semibold uppercase tracking-wide mb-1">Our Prediction</div>
                      <div className={`text-4xl sm:text-5xl font-black ${getOutcomeType(result.prediction).labelColor}`}>
                        {getOutcomeType(result.prediction).label}
                      </div>
                    </div>
                    <span className={`px-4 py-2 rounded-full text-sm font-bold border-2 ${getConfidenceBadge(result.confidence_score).color}`}>
                      {result.confidence_score}% Confident
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-6">
                  <div className="flex-1">
                    <h2 className="text-xl sm:text-2xl font-bold text-white mb-4">Detailed Analysis</h2>
                    <p className="text-base sm:text-lg text-gray-200 leading-relaxed mb-6">{result.prediction}</p>
                    
                    {/* Confidence Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm text-gray-300">
                        <span>Confidence Level</span>
                        <span className="font-bold text-xl text-white">{result.confidence_score}%</span>
                      </div>
                      <div className="relative w-full h-4 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
                        <div
                          className={`h-full rounded-full bg-gradient-to-r ${getConfidenceColor(result.confidence_score)} shadow-lg transition-all duration-1000 ease-out`}
                          style={{ width: `${result.confidence_score}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Data Quality Metrics */}
              {result.data_quality && (
                <div className="backdrop-blur-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-2 border-blue-400/30 rounded-3xl shadow-2xl p-6 sm:p-10">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-2xl">🎯</span>
                    Data Quality Analysis
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white/5 p-4 rounded-xl text-center">
                      <div className="text-3xl font-bold text-cyan-400">{result.data_quality.source_count}</div>
                      <div className="text-sm text-gray-300 mt-1">Total Sources</div>
                    </div>
                    <div className="bg-white/5 p-4 rounded-xl text-center">
                      <div className="text-3xl font-bold text-purple-400">{result.data_quality.platforms_used}</div>
                      <div className="text-sm text-gray-300 mt-1">Platforms</div>
                    </div>
                    <div className="bg-white/5 p-4 rounded-xl text-center">
                      <div className="text-3xl font-bold text-emerald-400">{result.data_quality.avg_quality_score}</div>
                      <div className="text-sm text-gray-300 mt-1">Avg Quality</div>
                    </div>
                    <div className="bg-white/5 p-4 rounded-xl text-center">
                      <div className="text-3xl font-bold text-yellow-400">+{result.data_quality.confidence_boost}</div>
                      <div className="text-sm text-gray-300 mt-1">Confidence Boost</div>
                    </div>
                  </div>
                  <div className="bg-white/5 p-4 rounded-xl">
                    <div className="text-sm font-semibold text-blue-300 mb-2">Platform Breakdown:</div>
                    <div className="flex flex-wrap gap-2">
                      {result.data_quality.platform_breakdown.map((platform, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-500/20 border border-blue-400/30 rounded-full text-sm text-blue-200">
                          {platform}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Key Factors */}
              {result.key_factors && result.key_factors.length > 0 && (
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-10">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-2xl">📊</span>
                    Key Evidence
                  </h3>
                  <div className="grid gap-4">
                    {result.key_factors.map((factor, index) => (
                      <div key={index} className="flex items-start gap-4 bg-white/5 p-4 rounded-xl backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
                        <span className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-white font-bold shadow-lg">
                          {index + 1}
                        </span>
                        <p className="text-gray-200 flex-1">{factor}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Caveats */}
              {result.caveats && result.caveats.length > 0 && (
                <div className="backdrop-blur-xl bg-amber-500/10 border-2 border-amber-500/30 rounded-3xl shadow-2xl p-6 sm:p-10">
                  <h3 className="text-2xl font-bold text-amber-200 mb-6 flex items-center gap-2">
                    <span className="text-2xl">⚠️</span>
                    Important Considerations
                  </h3>
                  <div className="space-y-3">
                    {result.caveats.map((caveat, index) => (
                      <div key={index} className="flex items-start gap-3 text-amber-100">
                        <span className="text-amber-400 text-xl">•</span>
                        <p>{caveat}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sources */}
              {result.sources && result.sources.length > 0 && (
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-10">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                    <span className="text-2xl">🔗</span>
                    Trusted Sources ({result.sources.length})
                  </h3>
                  <div className="grid gap-4">
                    {result.sources.slice(0, 8).map((source, index) => (
                      <div key={index} className="bg-white/5 p-5 rounded-xl backdrop-blur-sm hover:bg-white/10 transition-all duration-300 border border-white/10">
                        <div className="flex items-start gap-3 mb-2">
                          {source.reputation_badge && (
                            <span className="text-sm">{source.reputation_badge}</span>
                          )}
                          <h4 className="font-semibold text-white flex-1 line-clamp-2">{source.title}</h4>
                        </div>
                        <p className="text-gray-300 text-sm line-clamp-2 mb-2">{source.snippet}</p>
                        {source.source && (
                          <span className="text-xs text-gray-400 bg-white/5 px-2 py-1 rounded-full inline-block">
                            {source.source}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                  {result.sources.length > 8 && (
                    <p className="text-center text-gray-400 mt-4 text-sm">
                      + {result.sources.length - 8} more sources analyzed
                    </p>
                  )}
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
