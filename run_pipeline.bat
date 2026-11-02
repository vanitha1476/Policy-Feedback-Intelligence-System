@echo off
echo ======================================================================
echo Running End-to-End Policy Feedback Intelligence Pipeline (SIH25035)
echo ======================================================================
echo [1/6] Initializing SQLite database and loading comments...
python -m src.sql.db_manager
echo [2/6] Evaluating Stance and Sentiment Models...
python -m eval.evaluate_stance
echo [3/6] Detecting Astroturfing Campaigns ^& Near-Duplicates...
python -m src.dedupe.campaign_detector
echo [4/6] Generating Dual-Perspective TextRank Summaries...
python -m src.summarize.summarizer
echo [5/6] Mining Domain Keywords per Section ^& Stance...
python -m src.keywords.keyword_miner
echo [6/6] Generating Plain-English Executive Insights ^& Power BI Export...
python -m src.analytics.insight_generator
echo ======================================================================
echo Pipeline Execution Complete! All tables, views, and CSV exports updated.
echo ======================================================================
pause
