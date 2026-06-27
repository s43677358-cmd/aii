@echo off
REM AI Guardian OS - Unified Workflow Pipeline (Windows)

echo 🛡️ AI Guardian OS - Unified Workflow Pipeline
echo =============================================
echo.

echo 📦 Setting up local environment...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements_pipeline.txt

echo.
echo 🚀 Starting Streamlit application...
echo 📍 Application URL: http://localhost:8501
echo.

streamlit run pipeline_app.py --server.port=8501 --server.address=0.0.0.0
pause