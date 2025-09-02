#!/bin/bash
set -e

echo "🧪 Setting up Co-DataScientist frontend for testing..."

# Activate conda environment XOR
echo "🐍 Activating conda environment XOR..."
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate XOR
echo "✅ Conda environment XOR activated"

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

# 6. Run the frontend command with token reset
echo "🚀 Running frontend command with token reset..."
echo ""
echo "Command: uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/XOR/xor_solver.py"
echo ""

# Actually run the command
uv run main.py --dev run --script-path /home/ozkilim/Co-DataScientist_/XOR/xor_solver.py --python-path /home/ubuntu/miniconda3/envs/XOR/bin/python
