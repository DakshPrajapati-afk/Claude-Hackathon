# Confidence Scoring Guide

## How Confidence Scores Are Generated

The **confidence score** (0-100%) in the Poly Prediction Tool is determined by **Claude AI**, not by a mathematical formula. The AI evaluates the quality and consistency of evidence from multiple premium sources and assigns a confidence percentage.

---

## Updated Scoring Guidelines (Less Harsh)

The system has been updated to be **more generous** with confidence scores. Here are the guidelines Claude AI follows:

### 🟢 **85-100% - Very High Confidence**
**When to use:**
- Strong evidence from multiple reliable sources all support the same stance
- Clear trends with consistent data across sources
- Expert consensus or market indicators strongly favor one outcome

**Example scenarios:**
- 8 out of 10 news sources report positive earnings
- Market trends clearly up/down with strong momentum
- Expert predictions align with recent data

**What this means:** The prediction is very likely to be accurate. Strong consensus exists.

---

### 🟢 **70-84% - High Confidence**
**When to use:**
- Good evidence with clear trends
- Most sources support the stance, some uncertainty exists
- Historical patterns strongly suggest an outcome

**Example scenarios:**
- 6 out of 10 sources support the prediction
- Data shows clear direction but with some volatility
- Market sentiment is strong but not overwhelming

**What this means:** The prediction is likely accurate. There's a clear lean in one direction.

---

### 🔵 **55-69% - Moderate Confidence**
**When to use:**
- Moderate evidence exists
- One side is clearly stronger than the other (even if only slightly)
- Mixed signals but a discernible pattern emerges

**Example scenarios:**
- 5 out of 9 sources support the prediction
- Data shows a slight trend
- Some conflicting information but a winner emerges

**What this means:** The prediction has decent support. It's more likely than not, but uncertainty remains.

---

### 🟡 **40-54% - Low Confidence**
**When to use:**
- Limited evidence available
- Can still identify which side is marginally stronger
- Data is scarce but not completely absent

**Example scenarios:**
- 3 out of 5 sources lean one way
- Very recent news with limited historical data
- Emerging trends without strong confirmation

**What this means:** The prediction is a best guess with limited data. Roughly 50/50 but forced to choose.

---

### 🟠 **Below 40% - Very Low Confidence**
**When to use (RARE):**
- Highly speculative topics
- Almost no reliable data exists
- Pure guesswork based on minimal information

**Example scenarios:**
- Prediction about events 5+ years in the future
- Topics with no precedent or historical data
- Completely contradictory sources

**What this means:** This is a forced prediction with very little supporting evidence. High uncertainty.

---

## Key Improvements from Old System

### Old System (Too Harsh)
- **Problem:** AI was overly conservative
- **Result:** Most predictions got 40-60% confidence even with good evidence
- **User experience:** Felt like the system was never confident about anything

### New System (More Balanced)
- **Solution:** Clear guidelines with generous thresholds
- **Result:** Predictions with decent evidence get 60-80% confidence
- **User experience:** System feels confident when it should be

---

## How It Works Technically

### Backend (`app.py` - Lines 489-498)

The AI prompt includes explicit scoring guidelines:

```python
**CONFIDENCE SCORING GUIDELINES** (Be generous, not harsh):
- **85-100%**: Strong evidence from multiple reliable sources supports your stance
- **70-84%**: Good evidence with clear trends, some uncertainty exists
- **55-69%**: Moderate evidence, one side is stronger than the other
- **40-54%**: Limited evidence but you can still pick the more likely side
- **Below 40%**: Only use for highly speculative topics with almost no data

**IMPORTANT**: Having to choose between two options doesn't mean low confidence! 
If 3 out of 5 sources support YES, that's 70%+ confidence, not 50%.
```

### Frontend (`App.js` - Lines 43-49)

The UI displays confidence badges based on score ranges:

```javascript
const getConfidenceBadge = (score) => {
  if (score >= 85) return { text: 'Very High Confidence', ... };
  if (score >= 70) return { text: 'High Confidence', ... };
  if (score >= 55) return { text: 'Moderate Confidence', ... };
  if (score >= 40) return { text: 'Low Confidence', ... };
  return { text: 'Very Low Confidence', ... };
};
```

---

## Examples of Confidence Scoring

### Example 1: Bitcoin Price Prediction
**Query:** "Will Bitcoin reach $100k in 2025?"

**Data collected:**
- 7 financial news articles
- 5 positive sentiment (bullish)
- 1 negative sentiment (bearish)
- 1 neutral
- Yahoo Finance shows upward trend
- Reddit sentiment is positive

**Expected confidence:** **75-80%**
- Good evidence from multiple sources
- Clear positive trend (5/7 articles)
- Multiple data sources agree
- Historical patterns support it

---

### Example 2: Company Earnings
**Query:** "Will Tesla beat earnings expectations this quarter?"

**Data collected:**
- 3 news articles (all neutral/cautious)
- Yahoo Finance shows mixed signals
- Reddit has both bulls and bears
- No strong consensus

**Expected confidence:** **55-65%**
- Moderate evidence
- Slight lean toward one outcome
- Mixed signals but pattern emerges
- Decent data but no strong consensus

---

### Example 3: Long-term Tech Prediction
**Query:** "Will AI replace all software developers by 2030?"

**Data collected:**
- 4 opinion pieces (highly speculative)
- No historical precedent
- Wildly conflicting expert opinions
- Very limited concrete data

**Expected confidence:** **35-45%**
- Highly speculative topic
- Limited concrete evidence
- Prediction is more opinion than data-driven
- Too far in the future for certainty

---

## Why AI-Generated Scores?

### Advantages
✅ **Context-aware:** AI understands nuance in sources
✅ **Flexible:** Can adapt to different types of queries
✅ **Holistic:** Considers source quality, relevance, consistency
✅ **Natural:** Mimics how humans assess confidence

### Alternatives (Not Used)
❌ **Simple formulas:** `(positive_sources / total_sources) * 100`
   - Too rigid, doesn't account for source quality
   
❌ **Sentiment averages:** Average sentiment scores
   - Doesn't capture consistency or reliability
   
❌ **Fixed thresholds:** Hard-coded rules
   - Can't adapt to different query types

---

## Calibration Over Time

### Future Improvements
The confidence scoring can be calibrated over time by:

1. **Tracking Prediction Accuracy**
   - Store predictions with timestamps
   - Verify outcomes when events conclude
   - Compare predicted confidence vs actual accuracy

2. **Adjusting Guidelines**
   - If 70% confidence predictions are only 50% accurate → tighten guidelines
   - If 70% confidence predictions are 85% accurate → loosen guidelines

3. **Source Quality Weights**
   - Give more weight to historically accurate sources
   - Downweight sources with poor track records

---

## User Interpretation Guide

### When you see 85%+ confidence
- **Take it seriously:** Strong evidence supports this
- **Action:** High conviction decisions are reasonable
- **Caveat:** Still read the caveats section

### When you see 70-84% confidence
- **Good signal:** Clear trend identified
- **Action:** Moderate conviction decisions
- **Caveat:** Some uncertainty remains

### When you see 55-69% confidence
- **Slight edge:** More likely than not
- **Action:** Low conviction, be cautious
- **Caveat:** Significant uncertainty

### When you see 40-54% confidence
- **Toss-up:** Limited data available
- **Action:** Very low conviction, diversify
- **Caveat:** High uncertainty

### When you see <40% confidence
- **Speculation:** Not enough data
- **Action:** Avoid making decisions based on this
- **Caveat:** Extremely high uncertainty

---

## Testing the New System

To verify the improved scoring:

1. **Start the application**
2. **Test with these queries:**

   - **Should score 75%+:** "Will Apple's stock price increase in Q4 2024?"
   - **Should score 60-75%:** "Will Bitcoin reach $80k in 2025?"
   - **Should score 50-65%:** "Will there be a recession in 2026?"
   - **Should score <50%:** "Will AI replace all programmers by 2030?"

3. **Observe:** Scores should now be more generous for queries with decent evidence

---

## Summary

The Poly Prediction Tool now uses **more generous confidence scoring**:

- **Old system:** Conservative (most predictions 40-60%)
- **New system:** Balanced (decent evidence gets 60-80%)
- **Generated by:** Claude AI analyzing evidence
- **Guided by:** Clear scoring thresholds
- **Result:** More intuitive and useful confidence scores

The system **forces definitive predictions** (YES/NO) but **accurately reflects confidence** in those predictions.

