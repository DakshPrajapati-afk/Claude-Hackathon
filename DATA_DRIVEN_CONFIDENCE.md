# Data-Driven Confidence Scoring System

## Overview
The Poly Prediction Tool now uses a **hybrid confidence scoring system** that combines:
1. **Objective data metrics** (quantity, quality, diversity of sources)
2. **AI analysis** (strength of evidence and trends)

This ensures confidence scores are grounded in measurable data quality from Yahoo Finance, Reddit, Google, and NewsAPI.

---

## How It Works

### Step 1: Data Collection
When you make a query, the system gathers data from:
- **Google Custom Search** (web search results)
- **NewsAPI** (credible news articles)
- **Reddit** (community sentiment)
- **Yahoo Finance** (market data)
- **MarketWatch** (financial news)

Each source is tagged with:
- **Platform**: Which API it came from
- **Quality Score**: 0-100 based on source reputation
- **Relevance Score**: 0-100 based on query match
- **Reputation Badge**: Gold Star, Verified, etc.

### Step 2: Calculate Data Quality Baseline
Before AI analysis, the system calculates an **objective confidence baseline** (0-30 points):

#### Component 1: Source Quantity (0-10 points)
| Sources | Points | Grade |
|---------|--------|-------|
| 10+ | +10 | Excellent |
| 7-9 | +7 | Good |
| 4-6 | +4 | Moderate |
| 1-3 | +2 | Limited |

#### Component 2: Platform Diversity (0-10 points)
| Platforms | Points | Grade |
|-----------|--------|-------|
| 4-5 | +10 | Excellent diversity |
| 3 | +7 | Good diversity |
| 2 | +4 | Moderate diversity |
| 1 | +1 | Low diversity |

**Why diversity matters:** Data from Reddit + Yahoo Finance + NewsAPI + Google all agreeing is more reliable than 10 sources from just Google.

#### Component 3: Average Quality (0-10 points)
| Avg Quality | Points | Grade |
|-------------|--------|-------|
| 80-100 | +10 | High quality sources |
| 65-79 | +7 | Good quality sources |
| 50-64 | +4 | Moderate quality sources |
| <50 | +2 | Lower quality sources |

**Maximum Baseline: 30 points** (10 + 10 + 10)

### Step 3: AI Evidence Analysis
Claude AI then analyzes the actual content and adjusts confidence based on:

- **Strong supporting evidence**: +30 to +40 points
- **Clear trend**: +20 to +30 points
- **Moderate evidence**: +10 to +20 points
- **Weak evidence**: +0 to +10 points
- **Contradictory evidence**: -5 to 0 points

### Step 4: Final Confidence Score
```
Final Score = 40 (base) + Data Quality Baseline + AI Evidence Analysis
```

**Examples:**
- Base: 40 + Data: 27 (10 sources, 4 platforms, high quality) + AI: +30 (strong evidence) = **97% confidence**
- Base: 40 + Data: 15 (5 sources, 2 platforms, moderate quality) + AI: +15 (moderate evidence) = **70% confidence**
- Base: 40 + Data: 5 (3 sources, 1 platform, low quality) + AI: +5 (weak evidence) = **50% confidence**

---

## Backend Implementation

### Function: `calculate_data_driven_confidence(web_data)`
**Location:** `backend/app.py` (Lines 429-537)

```python
def calculate_data_driven_confidence(web_data):
    """
    Calculate objective confidence boost from data quality metrics.
    Returns: 0-30 point boost based on quantity, diversity, quality.
    """
    # Count sources by platform
    platform_counts = {
        'google': 0,
        'newsapi': 0,
        'reddit': 0,
        'yahoo_finance': 0,
        'marketwatch': 0
    }
    
    # Analyze each source
    for item in web_data:
        # Categorize by platform
        # Calculate quality and relevance
    
    # Return structured metrics
    return {
        'confidence_boost': 0-30,  # Objective boost
        'reasons': [...],          # Why this boost
        'platform_details': [...], # Platform breakdown
        'avg_quality': 0-100,      # Avg quality score
        'platforms_used': 1-5      # Number of platforms
    }
```

### Integration with AI Prompt
**Location:** `backend/app.py` (Lines 583-588)

The data metrics are passed to Claude AI:

```python
📊 DATA QUALITY METRICS (use these to inform your confidence score):
• Total Sources: 12
• Platforms Used: 4 (Google: 5, Newsapi: 3, Reddit: 2, Yahoo Finance: 2)
• Average Source Quality: 78/100
• Average Relevance: 85/100
• Base Confidence Adjustment: +27 points
```

Claude then sees explicit scoring guidelines:

```python
BASE SCORE CALCULATION:
1. Start with data quality baseline: 67% (40 + 27)
2. Adjust based on evidence strength:
   - Strong supporting evidence: +30 to +40 points → 85-100%
   - Clear trend: +20 to +30 points → 70-84%
   - Moderate evidence: +10 to +20 points → 55-69%
```

---

## Frontend Display

### Data Quality Card
**Location:** `frontend/src/App.js` (Lines 238-274)

A new card displays:

```
🎯 Data Quality Analysis

[12]        [4]         [78]        [+27]
Total     Platforms   Avg Quality  Confidence
Sources                            Boost

Platform Breakdown:
[Google: 5] [Newsapi: 3] [Reddit: 2] [Yahoo Finance: 2]
```

---

## Real-World Examples

### Example 1: Bitcoin Price Prediction

**Query:** "Will Bitcoin reach $100k in 2025?"

**Data Collected:**
- Google: 5 results (quality: 80)
- NewsAPI: 4 results (quality: 85)
- Yahoo Finance: 2 results (quality: 90)
- Reddit: 3 results (quality: 60)
- **Total:** 14 sources, 4 platforms

**Data Quality Calculation:**
- Source Quantity: 10+ sources = **+10 points**
- Platform Diversity: 4 platforms = **+10 points**
- Average Quality: (80×5 + 85×4 + 90×2 + 60×3) / 14 = 77 = **+7 points**
- **Baseline Boost: +27 points**

**AI Analysis:**
- 10 out of 14 sources bullish
- Clear upward trend in data
- Strong evidence for YES
- **AI Evidence Boost: +30 points**

**Final Confidence:**
```
40 (base) + 27 (data) + 30 (AI) = 97% confidence
```

**Result:** "YES - Bitcoin will reach $100k in 2025" with **97% confidence** ✅

---

### Example 2: Company Earnings

**Query:** "Will Tesla beat earnings this quarter?"

**Data Collected:**
- NewsAPI: 3 results (quality: 75)
- Google: 2 results (quality: 70)
- **Total:** 5 sources, 2 platforms

**Data Quality Calculation:**
- Source Quantity: 4-6 sources = **+4 points**
- Platform Diversity: 2 platforms = **+4 points**
- Average Quality: (75×3 + 70×2) / 5 = 73 = **+7 points**
- **Baseline Boost: +15 points**

**AI Analysis:**
- 3 sources positive, 2 neutral
- Slight upward trend
- Moderate evidence
- **AI Evidence Boost: +15 points**

**Final Confidence:**
```
40 (base) + 15 (data) + 15 (AI) = 70% confidence
```

**Result:** "HIGHLY LIKELY - Tesla will beat earnings" with **70% confidence** ✓

---

### Example 3: Speculative Tech Prediction

**Query:** "Will AI replace all programmers by 2030?"

**Data Collected:**
- Google: 2 results (quality: 65)
- Reddit: 2 results (quality: 50)
- **Total:** 4 sources, 2 platforms

**Data Quality Calculation:**
- Source Quantity: 4 sources = **+4 points**
- Platform Diversity: 2 platforms = **+4 points**
- Average Quality: (65×2 + 50×2) / 4 = 57.5 = **+4 points**
- **Baseline Boost: +12 points**

**AI Analysis:**
- Sources wildly contradictory
- No clear trend
- Highly speculative topic
- **AI Evidence Boost: -2 points**

**Final Confidence:**
```
40 (base) + 12 (data) + (-2) (AI) = 50% confidence
```

**Result:** "NO - AI will not replace all programmers by 2030" with **50% confidence** ⚠️

---

## Benefits of Data-Driven Scoring

### ✅ Objective Foundation
- Confidence is grounded in **measurable metrics**
- Not just AI "gut feeling"
- Users can see **why** the confidence is high/low

### ✅ Platform Transparency
- Users see which platforms contributed
- Understand the **diversity** of data sources
- Trust the prediction more with diverse sources

### ✅ Quality Visibility
- Average quality scores shown
- Users can judge if sources are credible
- **High-quality sources = higher confidence**

### ✅ Reproducible
- Same data inputs = same baseline score
- AI analysis varies but data metrics don't
- More **consistent** over time

### ✅ User Education
- Users learn what makes a good prediction
- Understand importance of **multiple platforms**
- Appreciate **quality over quantity**

---

## API Response Structure

```json
{
  "prediction": "YES - Bitcoin will reach $100k...",
  "confidence_score": 85,
  "key_factors": [...],
  "caveats": [...],
  "data_quality": {
    "source_count": 12,
    "platforms_used": 4,
    "platform_breakdown": [
      "Google: 5",
      "Newsapi: 3",
      "Reddit: 2",
      "Yahoo Finance: 2"
    ],
    "avg_quality_score": 78.5,
    "avg_relevance_score": 82.3,
    "confidence_boost": 27
  },
  "sources": [...]
}
```

---

## Debugging Confidence Scores

If you think a confidence score is wrong:

### 1. Check Data Quality Metrics
Look at the `data_quality` object:
- **Low source_count?** Not enough data gathered
- **Low platforms_used?** Missing API keys or query too narrow
- **Low avg_quality_score?** Sources are low-reputation
- **Low confidence_boost?** All of the above

### 2. Check Platform Breakdown
See which platforms contributed:
- **Only Google?** Other APIs may have failed
- **No Yahoo Finance?** Query might not be financial
- **No Reddit?** Query might not have community discussion
- **No NewsAPI?** Query might be too niche

### 3. Check Backend Logs
The backend prints detailed analysis:
```
📊 DATA QUALITY ANALYSIS:
   ✓ Excellent data: 12 sources
   ✓ Excellent diversity: 4 platforms
   ✓ High quality sources: 78/100
   Platforms: Google: 5, Newsapi: 3, Reddit: 2, Yahoo Finance: 2
   Base Confidence Boost: +27 points
```

### 4. Check AI Reasoning
Look at `key_factors`:
- Do they support the prediction?
- Is the evidence strong or weak?
- Does the AI explain its confidence level?

---

## Tuning the System

If you want to adjust confidence scoring:

### Make Confidence More Generous
In `backend/app.py`, increase baseline:
```python
# Line 620
1. Start with data quality baseline: {40 + data_metrics['confidence_boost']}%
# Change 40 to 45 or 50 for higher baseline
```

### Make Confidence More Conservative
Decrease baseline:
```python
# Change 40 to 35 or 30 for lower baseline
```

### Adjust Platform Diversity Weight
In `calculate_data_driven_confidence()`:
```python
# Lines 494-506
# Increase max points for diversity (currently 10)
if platforms_used >= 4:
    confidence_boost += 15  # Was 10
```

### Adjust Quality Weight
```python
# Lines 508-520
# Increase max points for quality (currently 10)
if avg_quality >= 80:
    confidence_boost += 15  # Was 10
```

---

## Summary

The **Data-Driven Confidence System** ensures predictions are backed by:

1. ✅ **Measurable data quality** from Yahoo Finance, Reddit, Google, NewsAPI
2. ✅ **Platform diversity** (more platforms = more confidence)
3. ✅ **Source reputation** (quality scoring)
4. ✅ **Transparent metrics** (users see the breakdown)
5. ✅ **AI analysis** (combines data quality with evidence strength)

**Result:** Confidence scores you can trust, backed by real data! 🎯

