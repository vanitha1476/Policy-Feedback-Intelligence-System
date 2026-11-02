@echo off
echo ======================================================================
echo Launching Policy ^& Regulatory Feedback Intelligence Dashboard
echo ======================================================================
python -m streamlit run app/dashboard.py --server.headless=false
pause
