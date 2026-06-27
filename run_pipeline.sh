#!/bin/bash

echo "🛡️ AI Guardian OS - Unified Workflow Pipeline"
echo "============================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "✅ Running in Docker container"
else
    echo "📦 Setting up local environment..."
    python -m venv venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
    pip install -r requirements_pipeline.txt
fi

echo ""
echo "🚀 Starting Streamlit application..."
echo "📍 Application URL: http://localhost:8501"
echo ""

streamlit run pipeline_app.py --server.port=8501 --server.address=0.0.0.0
