# 📊 Data Quality & Source Verification Guide

## Overview

Your prediction tool now has a **comprehensive data quality system** that ensures you're getting accurate, reputable information from multiple sources.

---

## 🎯 How It Works

### **Multi-Layered Quality System:**

```
User Query
    ↓
[1] Query Enhancement (add relevant keywords)
    ↓
[2] Multi-Source Gathering (NewsAPI, MarketWatch, DuckDuckGo)
    ↓
[3] Source Quality Scoring (Tier 1-4 reputation system)
    ↓
[4] Spam/Clickbait Filtering
    ↓
[5] Relevance Matching
    ↓
[6] Quality Ranking
    ↓
Top 10 Highest Quality, Most Relevant Sources
```

---

## 🏆 Source Reputation Tiers

### **Tier 1: 🏆 Highly Trusted** (Score: 100)
**Major news organizations with strong fact-checking**

- **News:** Reuters, AP, Bloomberg, WSJ, NYT, Washington Post, BBC, Guardian
- **Finance:** MarketWatch, Financial Times, Barron's
- **Tech:** MIT Technology Review, Nature, Science
- **Fact-Checking:** PolitiFact, FactCheck.org, Snopes

**Why Tier 1?**
- Professional newsrooms
- Multiple layers of editorial oversight
- Established fact-checking processes
- Corrections policy
- Long history of accuracy

### **Tier 2: ✅ Trusted** (Score: 80)
**Established publications**

- CNN, NBC, CBS, ABC, Fox News
- TIME, Newsweek, Axios, Politico
- CNBC, Forbes, Fortune
- TechCrunch, The Verge, Wired

**Why Tier 2?**
- Professional journalism
- Editorial standards
- Generally reliable but occasional bias

### **Tier 3: ⚠️ Verify Claims** (Score: 60)
**Popular but require verification**

- Medium, Substack (varies by author)
- BuzzFeed News
- HuffPost, Slate

**Why Tier 3?**
- Mix of quality content
- Less rigorous fact-checking
- More opinion-based
- Verify important claims

### **Tier 4: ❓ Unknown Source** (Score: 40)
**Unverified web sources**

- General web search results
- Unknown domains
- New publications

**Why Tier 4?**
- No established reputation
- Unknown editorial standards
- Requires cross-referencing

---

## 🔍 Quality Scoring Algorithm

Each source gets a quality score (0-100) based on:

### **1. Source Reputation (50%)**
```
Tier 1: 100 points → 50 score contribution
Tier 2: 80 points  → 40 score contribution
Tier 3: 60 points  → 30 score contribution
Tier 4: 40 points  → 20 score contribution
```

### **2. Relevance (30%)**
```
- Counts query words in title/description
- More matches = higher relevance
- 0-10 scale → 0-30 points
```

### **3. Recency (20%)**
```
1 day old:    20 points
7 days old:   15 points
30 days old:  10 points
Older:        5 points
```

### **Example Calculation:**
```
Reuters article (Tier 1):
- Source reputation: 100 * 0.5 = 50 points
- Relevance (8/10):   8 * 3 =   24 points
- Recency (2 days):              15 points
─────────────────────────────────
TOTAL:                           89/100
```

---

## 🛡️ Spam & Clickbait Filtering

### **Automatically Filtered:**

❌ Articles containing these phrases:
- "You won't believe..."
- "Doctors hate this..."
- "One weird trick..."
- "Click here now..."
- "Shocking revelation..."
- "Get rich quick..."

❌ Other filters:
- Titles shorter than 15 characters
- Duplicate content
- Blacklisted domains
- Articles with no description

---

## 📈 Query Enhancement

The system automatically improves your queries for better results:

### **Example 1: Election Query**
```
Input:  "Who will win?"
Enhanced: "Who will win? latest poll candidate campaign"
```

### **Example 2: Financial Query**
```
Input:  "Bitcoin price"
Enhanced: "Bitcoin price latest cryptocurrency blockchain market"
```

### **Example 3: Tech Query**
```
Input:  "AI development"
Enhanced: "AI development latest AI software innovation technology"
```

**Topics Detected:**
- Elections → adds poll, candidate, campaign keywords
- Economy → adds GDP, inflation, market keywords
- Crypto → adds blockchain, cryptocurrency keywords
- Politics → adds policy, legislation keywords
- Tech → adds AI, software, innovation keywords
- Climate → adds emissions, renewable keywords
- Health → adds medical, treatment keywords

---

## 🔧 How to Ensure Data Quality

### **1. Add NewsAPI Key (Recommended)**

NewsAPI provides the highest quality sources:

```bash
# Get free key: https://newsapi.org/
# Add to .env file:
echo 'NEWS_API_KEY=your_key_here' >> .env
```

**Benefits:**
- ✅ Access to 80,000+ news sources
- ✅ Professional news only
- ✅ Last 30 days of articles
- ✅ Sorted by relevance
- ✅ Free tier: 100 requests/day

### **2. Use Specific Queries**

❌ **Vague:** "Who will win?"
✅ **Specific:** "2024 US presidential election polling data"

❌ **Vague:** "Stock market"
✅ **Specific:** "S&P 500 market forecast Q4 2024"

❌ **Vague:** "AI news"
✅ **Specific:** "GPT-4 capabilities enterprise adoption"

### **3. Check Source Quality in Results**

Look for the reputation badges in sources:
- 🏆 **Highly Trusted** → Use with confidence
- ✅ **Trusted** → Generally reliable
- ⚠️ **Verify Claims** → Cross-reference important facts
- ❓ **Unknown Source** → Verify with other sources

### **4. Monitor Backend Logs**

When you make a prediction, check the terminal for quality report:

```
🔍 GATHERING DATA
   Original query: 'election prediction'
   Enhanced query: 'election prediction latest poll candidate'

  📰 NewsAPI:
     ✓ 8 quality articles
       • Reuters 🏆 Highly Trusted
       • BBC News 🏆 Highly Trusted
       • The Guardian 🏆 Highly Trusted

  ✅ QUALITY FILTERED RESULTS: 10
     🏆 Tier 1 (Highly Trusted): 6
     ✅ Tier 2 (Trusted): 3
     ⚠️  Tier 3 (Verify): 1
     ❓ Tier 4 (Unknown): 0
     📊 Average Quality Score: 82.5/100
```

### **5. Use Debug Endpoint**

Test what sources you're getting:

```bash
curl -X POST http://localhost:5001/api/debug/sources \
  -H "Content-Type: application/json" \
  -d '{"query": "your test query"}'
```

**Returns:**
```json
{
  "original_query": "election prediction",
  "enhanced_query": "election prediction latest poll",
  "total_sources_found": 10,
  "sources": [
    {
      "title": "Latest Election Polls Show...",
      "source": "Reuters",
      "reputation_badge": "🏆 Highly Trusted",
      "source_tier": 1,
      "quality_score": 89.5,
      "sentiment": "neutral"
    }
  ]
}
```

---

## 📊 Interpreting Results

### **High Quality Results (80-100 score)**
- ✅ Majority Tier 1-2 sources
- ✅ Average quality score > 75
- ✅ Multiple sources confirm facts
- ✅ Recent articles (< 7 days)

**→ High confidence in prediction**

### **Medium Quality Results (60-79 score)**
- ⚠️ Mix of Tier 2-3 sources
- ⚠️ Average quality score 60-75
- ⚠️ Some sources unverified
- ⚠️ Older articles (> 7 days)

**→ Moderate confidence, verify key claims**

### **Low Quality Results (< 60 score)**
- ❌ Mostly Tier 3-4 sources
- ❌ Average quality score < 60
- ❌ Few reputable sources
- ❌ Very old or no relevant articles

**→ Low confidence, need better sources**

---

## 🎯 Best Practices

### **DO:**
✅ Use specific, detailed queries
✅ Add NewsAPI key for best results
✅ Check source reputation badges
✅ Monitor backend quality reports
✅ Cross-reference important claims
✅ Prefer recent articles

### **DON'T:**
❌ Trust single-source predictions
❌ Ignore reputation badges
❌ Use vague queries
❌ Rely on old data for time-sensitive queries
❌ Skip verification for important decisions

---

## 🔬 Quality Assurance Checklist

Before trusting a prediction, verify:

- [ ] **Multiple Sources:** At least 3-5 sources confirm
- [ ] **Source Quality:** Majority Tier 1-2 sources
- [ ] **Recent Data:** Articles within last 30 days
- [ ] **High Quality Score:** Average > 70
- [ ] **Relevant Content:** Sources actually address query
- [ ] **Sentiment Consistency:** Similar sentiment across sources
- [ ] **No Spam:** Filtered clickbait content

---

## 🛠️ Customizing Quality Standards

You can modify source tiers in `source_quality.py`:

### **Add New Trusted Sources:**
```python
TIER_1_SOURCES = {
    'Reuters', 'AP', ...
    'Your Trusted Source'  # Add here
}
```

### **Blacklist Domains:**
```python
BLACKLISTED_DOMAINS = {
    'known-fake-news.com',
    'spam-site.com'
}
```

### **Adjust Quality Weights:**
```python
# In calculate_quality_score():
# Change weights: reputation, relevance, recency
final_score = (tier_score * 0.5) + relevance_contribution + recency_contribution
#                          ↑ 50% weight - adjust as needed
```

---

## 📈 Monitoring Data Quality

### **Real-Time Monitoring:**

Watch backend terminal for:
- ✅ Number of sources found
- ✅ Source tier distribution
- ✅ Average quality score
- ✅ Spam filtered count
- ⚠️ API errors or failures

### **Database Analysis:**

```sql
-- Average quality by source
SELECT source, AVG(quality_score) 
FROM sources 
GROUP BY source 
ORDER BY AVG(quality_score) DESC;

-- Confidence vs Source Quality correlation
SELECT 
    CASE 
        WHEN quality_score >= 80 THEN 'High'
        WHEN quality_score >= 60 THEN 'Medium'
        ELSE 'Low'
    END as quality_tier,
    AVG(confidence_score) as avg_confidence
FROM predictions p
JOIN sources s ON p.query_id = s.query_id
GROUP BY quality_tier;
```

---

## 🎓 Understanding Limitations

### **What This System CAN Do:**
✅ Filter low-quality sources
✅ Prioritize reputable outlets
✅ Remove spam/clickbait
✅ Match relevance to query
✅ Rank by multiple quality factors

### **What This System CANNOT Do:**
❌ Guarantee 100% accuracy
❌ Detect all misinformation
❌ Replace human judgment
❌ Verify facts independently
❌ Detect subtle bias

**→ Always apply critical thinking!**

---

## 🚀 Quick Commands

```bash
# Test source quality
curl -X POST http://localhost:5001/api/debug/sources \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'

# View backend quality reports
tail -f backend_terminal_output

# Check which sources are Tier 1
grep "TIER_1" backend/source_quality.py

# Monitor predictions
curl http://localhost:5001/api/stats
```

---

## 📚 Additional Resources

- **NewsAPI Documentation:** https://newsapi.org/docs
- **MarketWatch RSS:** https://www.marketwatch.com/rss
- **Source Verification:** https://www.poynter.org/
- **Media Bias Chart:** https://adfontesmedia.com/

---

## 💡 Pro Tips

1. **For Elections:** Add "poll" or "polling data" to queries
2. **For Finance:** Add specific ticker symbols or market names
3. **For Breaking News:** Add "breaking" or "latest update"
4. **For Analysis:** Add "analysis" or "expert opinion"
5. **For Facts:** Add "data" or "statistics"

---

## ✅ Summary

Your system now ensures data quality through:

1. ✅ **Multi-source aggregation** (NewsAPI, MarketWatch, Web)
2. ✅ **4-tier reputation system** (Highly Trusted → Unknown)
3. ✅ **Quality scoring** (0-100 based on reputation + relevance + recency)
4. ✅ **Spam filtering** (clickbait detection)
5. ✅ **Query enhancement** (automatic keyword addition)
6. ✅ **Relevance matching** (only includes matching content)
7. ✅ **Debug tools** (see exactly what's being found)
8. ✅ **Real-time monitoring** (quality reports in terminal)

**Result: High-quality, reputable sources for accurate predictions!** 🎯

