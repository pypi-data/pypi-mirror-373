#!/bin/bash
set -e

echo "🧪 Testing Co-DataScientist frontend with BEST-ONLY mode and BATCH EXECUTION..."

# Activate conda environment XOR
echo "🐍 Activating conda environment ppi..."
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate ppi
echo "✅ Conda environment ppi activated"

# 1. Load API keys if available (go up one level)
if [[ -f "../api-keys.env" ]]; then
    echo "🔑 Loading API keys..."
    source ../api-keys.env
else
    echo "⚠️  No api-keys.env found - using default settings"
fi

# 2. Set dev mode (skip if .env already exists)
if [[ ! -f ".env" ]]; then
    echo "🔧 Setting up dev mode..."
    cd .. && ./mode-switch.sh dev && cd co-datascientist
else
    echo "✅ Dev mode already configured (found .env file)"
fi

# 3. Use hardcoded test token
echo "🎫 Using hardcoded test token..."
TEST_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJURVNUIiwiZXhwIjoxNzUzMjc5Nzc5LCJpYXQiOjE3NTA2ODc3Nzl9.60uRWjigkwm4ZI_eSCerbFOZyaUMGngZ4ZVO1fqlRSM"

# 4. Export token for this session
export API_KEY="$TEST_TOKEN"
echo "✅ Token set: ${TEST_TOKEN:0:20}..."

# 5. Check if backend is running, if not start it
echo "🔍 Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "🚀 Starting backend..."
    cd ../co-datascientist-backend
    uv run main.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    
    # Wait a bit for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    cd ../co-datascientist
else
    echo "✅ Backend is already running"
fi

# 6. Batch Execution Tests
echo ""
echo "🚀 BATCH EXECUTION TESTS"
echo "========================"

# Test 1: Sequential Mode (batch_size=1) - Original behavior
echo ""
echo "📝 TEST 1: Sequential Mode (batch_size=1)"
echo "Command: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --best-only --checkpoint-interval 5 --batch-size 1"
echo ""
# Uncomment to run: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 1

# Test 2: Small Batch Mode (batch_size=2)
echo ""
echo "📝 TEST 2: Small Batch Mode (batch_size=2)"
echo "Command: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --best-only --checkpoint-interval 5 --batch-size 2 --max-concurrent 2"
echo ""
# Uncomment to run: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 2 --max-concurrent 2

# Test 3: Large Batch Mode (batch_size=4) - The epic parallel test!
echo ""
echo "📝 TEST 3: Large Batch Mode (batch_size=4) - EPIC PARALLEL EXECUTION! 🚀"
echo "Command: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --best-only --checkpoint-interval 3 --batch-size 4 --max-concurrent 3"
echo ""

echo "🎯 Choose which test to run:"
echo "1) Sequential Mode (batch_size=1)"
echo "2) Small Batch Mode (batch_size=2)" 
echo "3) Large Batch Mode (batch_size=4) - RECOMMENDED!"
echo "4) Run Test 1 (sequential) automatically"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Running Test 1: Sequential Mode..."
        uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 1
        ;;
    2) 
        echo "🚀 Running Test 2: Small Batch Mode..."
        uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 2 --max-concurrent 2
        ;;
    3)
        echo "🚀 Running Test 3: Large Batch Mode - EPIC PARALLEL! ⚡"
        uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 3 --batch-size 4 --max-concurrent 3
        ;;
    4)
        echo "🚀 Auto-running Test 1: Sequential Mode..."
        uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 1
        ;;
    *)
        echo "❌ Invalid choice. Running Test 1 (sequential) as default..."
        uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/ppi_demo/ppi.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 1
        ;;
esac

echo ""
echo "✅ Test completed!" 


uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/demos/MPPE1/baseline.py --python-path /home/ubuntu/miniconda3/bin/python --best-only --checkpoint-interval 5 --batch-size 10 --max-concurrent 2

