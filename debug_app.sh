#!/bin/bash
# Debug Script for Prediction Tool
# This will identify why the application isn't working

echo "🔍 PREDICTION TOOL DIAGNOSTIC TOOL"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test 1: Check if .env file exists
echo "Test 1: Checking .env file..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    PASSED=$((PASSED+1))
    
    # Check if API key is set
    if grep -q "ANTHROPIC_API_KEY" .env; then
        API_KEY=$(grep "ANTHROPIC_API_KEY" .env | cut -d'=' -f2)
        if [ -z "$API_KEY" ] || [ "$API_KEY" = "your_api_key_here" ]; then
            echo -e "${RED}✗${NC} API key is not set or is placeholder"
            echo "  FIX: Add your real API key to .env file"
            FAILED=$((FAILED+1))
        else
            echo -e "${GREEN}✓${NC} API key is configured"
            PASSED=$((PASSED+1))
        fi
    else
        echo -e "${RED}✗${NC} ANTHROPIC_API_KEY not found in .env"
        echo "  FIX: Add ANTHROPIC_API_KEY=your_key to .env"
        FAILED=$((FAILED+1))
    fi
else
    echo -e "${RED}✗${NC} .env file does not exist"
    echo "  FIX: Create .env file with: echo 'ANTHROPIC_API_KEY=your_key' > .env"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 2: Check if backend is running
echo "Test 2: Checking if backend is running..."
HEALTH_CHECK=$(curl -s http://localhost:5000/api/health 2>&1)
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}✓${NC} Backend is running and healthy"
    PASSED=$((PASSED+1))
else
    echo -e "${RED}✗${NC} Backend is not running or not responding"
    echo "  FIX: Start backend with:"
    echo "       cd backend && source venv/bin/activate && python app.py"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 3: Check if frontend is running
echo "Test 3: Checking if frontend is running..."
FRONTEND_CHECK=$(curl -s http://localhost:3000 2>&1)
if [[ $FRONTEND_CHECK == *"html"* ]] || [[ $FRONTEND_CHECK == *"<!DOCTYPE"* ]]; then
    echo -e "${GREEN}✓${NC} Frontend is running"
    PASSED=$((PASSED+1))
else
    echo -e "${YELLOW}⚠${NC} Frontend may not be running"
    echo "  FIX: Start frontend with: cd frontend && npm start"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 4: Check Python dependencies
echo "Test 4: Checking Python dependencies..."
if [ -d "backend/venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    PASSED=$((PASSED+1))
    
    # Check if packages are installed
    cd backend
    source venv/bin/activate
    PACKAGES_OK=true
    
    for package in flask anthropic sqlalchemy requests beautifulsoup4; do
        if python -c "import $package" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $package installed"
        else
            echo -e "  ${RED}✗${NC} $package NOT installed"
            PACKAGES_OK=false
        fi
    done
    
    if [ "$PACKAGES_OK" = true ]; then
        PASSED=$((PASSED+1))
    else
        FAILED=$((FAILED+1))
        echo "  FIX: cd backend && pip install -r requirements.txt"
    fi
    cd ..
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    echo "  FIX: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    FAILED=$((FAILED+1))
fi
echo ""

# Test 5: Test API endpoint directly
echo "Test 5: Testing API prediction endpoint..."
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    PREDICTION_TEST=$(curl -s -X POST http://localhost:5000/api/predict \
        -H "Content-Type: application/json" \
        -d '{"query": "Test"}' 2>&1)
    
    if [[ $PREDICTION_TEST == *"error"* ]]; then
        echo -e "${RED}✗${NC} API returned an error"
        echo "  Error response: $PREDICTION_TEST"
        FAILED=$((FAILED+1))
        
        # Check for specific errors
        if [[ $PREDICTION_TEST == *"API key"* ]] || [[ $PREDICTION_TEST == *"authentication"* ]]; then
            echo -e "${YELLOW}⚠${NC} Likely cause: Invalid or missing API key"
            echo "  FIX: Check your ANTHROPIC_API_KEY in .env file"
        fi
    elif [[ $PREDICTION_TEST == *"prediction"* ]]; then
        echo -e "${GREEN}✓${NC} API endpoint working correctly"
        PASSED=$((PASSED+1))
    else
        echo -e "${YELLOW}⚠${NC} Unexpected API response"
        echo "  Response: ${PREDICTION_TEST:0:200}..."
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping (backend not running)"
fi
echo ""

# Test 6: Check database
echo "Test 6: Checking database..."
if [ -f "backend/predictions.db" ]; then
    echo -e "${GREEN}✓${NC} Database file exists"
    PASSED=$((PASSED+1))
    
    # Check if database is accessible
    DB_CHECK=$(sqlite3 backend/predictions.db "SELECT name FROM sqlite_master WHERE type='table';" 2>&1)
    if [[ $DB_CHECK == *"queries"* ]] && [[ $DB_CHECK == *"predictions"* ]]; then
        echo -e "${GREEN}✓${NC} Database tables exist"
        PASSED=$((PASSED+1))
    else
        echo -e "${RED}✗${NC} Database tables missing"
        echo "  FIX: cd backend && python database.py"
        FAILED=$((FAILED+1))
    fi
else
    echo -e "${YELLOW}⚠${NC} Database file doesn't exist yet (will be created on first run)"
fi
echo ""

# Summary
echo "===================================="
echo "DIAGNOSTIC SUMMARY"
echo "===================================="
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Your application should be working.${NC}"
    echo ""
    echo "If you're still seeing errors, check:"
    echo "  1. Browser console (F12) for JavaScript errors"
    echo "  2. Backend terminal for Python errors"
    echo "  3. Network tab in browser to see API responses"
else
    echo -e "${RED}⚠ Some tests failed. Fix the issues above and try again.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  1. Make sure .env file has valid ANTHROPIC_API_KEY"
    echo "  2. Start backend: cd backend && source venv/bin/activate && python app.py"
    echo "  3. Start frontend: cd frontend && npm start"
fi
echo ""

