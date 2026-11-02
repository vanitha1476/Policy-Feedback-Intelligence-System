# Policy & Regulatory Feedback Intelligence System

> **This tool reads public comments on a draft law and shows what people feel about each clause. It also finds fake or copy-paste campaign comments, so decision makers can see the real public opinion.**

---

## 📌 What This Project Does

When governments publish draft laws for public consultation, they receive thousands of feedback comments. Reading all of them manually takes weeks and is vulnerable to coordinated astroturfing campaigns (where special-interest groups submit thousands of copy-pasted form letters to create a false impression of public outrage or support).

This system provides a local, offline decision-support tool that:
1. **Identifies the specific clause or section** each comment is talking about.
2. **Predicts public stance** (Support, Oppose, or Neutral) with calibrated confidence scores.
3. **Detects astroturfing & coordinated copy-paste campaigns** using text similarity clustering, giving decision-makers both raw and campaign-adjusted sentiment.
4. **Generates short AI summaries** for each clause, clearly separating key supporting arguments from key concerns and objections.
5. **Ranks clauses by controversy** using mathematical polarization scoring so officials know which clauses need immediate attention.
6. **Enables fast search and report exports** so officers can filter comments by clause or sentiment and download CSV or executive briefing reports.

---

## 🧭 Dashboard Tabs

The interactive dashboard is organized into 7 simple, clean tabs:

| Tab | What You Can Do |
| :--- | :--- |
| **📊 Overview** | View top numbers at a glance (Total Comments, Positive %, Neutral %, Negative %, Flagged Campaigns), submission velocity over time, and raw vs. adjusted sentiment. |
| **📜 Clauses** | Select any clause of the draft bill to see its statutory text, a clause sentiment donut chart, and an AI summary with key support points and key objections. |
| **💬 Sentiment** | Compare sentiment across all draft clauses using stacked bar charts and summary tables. |
| **🛡️ Campaigns** | View copy-paste form-letter campaigns, see why each was flagged (e.g. text similarity ≥75%), and inspect original vs. duplicate submissions. |
| **💡 Insights** | Review plain-English strategic findings and the Controversy Index Ranking (entropy × volume) to find the most polarized clauses. |
| **📁 Data & Export** | Search comments with keywords, filter by clause, stance, or campaign status, and export filtered data as CSV or formatted executive report. |
| **🎯 Evaluation** | Inspect model accuracy and F1 benchmark metrics, and use the Live Feedback Tester to run predictions on live stakeholder comments in real time. |

---

## 📊 Model Accuracy & Benchmark Performance

On evaluation benchmarks, the system compares domain-trained machine learning against standard sentiment analysis:

| Model Architecture | Macro-F1 (%) | Accuracy (%) | Support F1 | Neutral F1 | Oppose F1 | Speed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF + Logistic Regression (Selected)** | **93.3%** | **93.3%** | 88.9% | 90.9% | 100.0% | < 1 ms |
| **TF-IDF + Linear SVM (Calibrated)** | **96.7%** | **96.7%** | 94.7% | 95.2% | 100.0% | < 2 ms |
| **VADER Lexical Sentiment (Baseline)** | **66.8%** | **66.7%** | 63.6% | 63.2% | 73.7% | < 1 ms |

> **Why standard sentiment analysis fails on legal feedback:**
> Off-the-shelf sentiment tools (like VADER) have a **49.3% disconnect rate** on policy comments. They misclassify critical words (such as *"draconian penalties"* or *"punish gatekeepers"*) as opposition, when citizens are actually using strong language to **support** strict regulatory intervention. Our trained stance classifier accurately captures the policy context.

---

## ⚡ How to Install and Run

### 1. Prerequisites
- **Python 3.10+** installed on your system.

### 2. Install Dependencies
Open a command prompt in the project root directory and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
Double-click `run_dashboard.bat` or run:
```bash
streamlit run app/dashboard.py
```
Open your browser and navigate to:
```
http://localhost:8501
```

### 4. Run the Full Data Pipeline (Optional)
To re-ingest comments, update SQLite tables, run clustering, and generate reports:
```bash
run_pipeline.bat
```

### 5. Run Unit Tests
```bash
python -m pytest
```
*All 10 unit tests pass in under 4 seconds.*

---

## 📁 Repository Structure

```plaintext
NLP PROJECT/
├── app/
│   ├── dashboard.py              # Main Streamlit dashboard application
│   └── ui_components.py         # Modular UI components, charts, and renderers
├── config/
│   └── config.yaml               # Global configurations and threshold settings
├── data/
│   ├── consultation.db           # SQLite database with all tables and views
│   ├── draft_sections/           # Draft statutory text JSON
│   ├── processed/                # Normalized comments corpus
│   └── raw/                      # External benchmark datasets
├── eval/
│   ├── evaluate_linking.py       # Clause linker accuracy and ablation tests
│   └── evaluate_stance.py        # Model stance and sentiment evaluation suite
├── reports/
│   ├── stance_evaluation.md      # Detailed model comparison report
│   ├── executive_insights.md     # Plain-English executive briefing
│   └── campaign_dedup_report.md  # Astroturfing cluster breakdown
├── src/
│   ├── analytics/                # Controversy ranking and insight generator
│   ├── dedupe/                   # Cosine similarity and graph campaign detector
│   ├── ingest/                   # PII cleaning and synthetic data generator
│   ├── keywords/                 # TF-IDF keyword extraction
│   ├── linking/                  # 4-tier hybrid clause linker
│   ├── models/                   # Stance classifiers (LR, SVM, VADER, DistilBERT)
│   ├── sql/                      # SQLite schema, tables, and views
│   └── summarize/                # Dual-perspective TextRank summarizer
├── tests/                        # 10 automated unit tests (100% passing)
├── requirements.txt              # Python package requirements
├── run_dashboard.bat             # Batch launcher for dashboard
├── run_pipeline.bat              # Batch launcher for pipeline
└── README.md                     # Project documentation
```
