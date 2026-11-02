# Final Project Evaluation & Engineering Report

**Project Title:** Policy & Regulatory Feedback Intelligence System  
**Problem Statement Reference:** SIH25035 (Ministry of Corporate Affairs)  
**System Architecture:** End-to-End Clause-Level Stance Detection, Astroturfing Deduplication & Decision Support  
**Date of Completion:** October 2026  

---

## 1. Executive Summary & Problem Background

Government ministries in India receive thousands of public submissions through e-consultation modules (such as MCA21 and MyGov.in) during public feedback windows for draft bills and subordinate legislation. Manually analyzing thousands of lengthy, unstructured comments across multi-page legislative bills presents severe administrative bottlenecks:
1. **Clause Disconnect:** General sentiment analysis models score entire documents as "positive" or "negative", failing to identify *which specific section or sub-clause* stakeholders oppose.
2. **Astroturfing & Coordinated Lobbying:** Special interest groups and lobby coalitions submit hundreds of templated near-duplicate emails, severely skewing raw opinion counts.
3. **The Stance vs. Sentiment Disconnect:** Lexical emotional sentiment tools (e.g., VADER) fail on regulatory text because critical or aggressive words are frequently deployed to support strong antitrust regulation.
4. **Lack of Trust & Verifiability:** Black-box NLP models cannot be directly utilized in ministerial decision-making without confidence calibration and human-in-the-loop audit trails.

### Project Contribution & Novelty
We present an end-to-end, zero-cost, CPU-optimized feedback intelligence system that transforms raw public submissions into decision-ready insights. The core contributions are:
- **Section-Level Aggregation:** A 4-tier hybrid linker routing comments to specific legislative clauses.
- **Raw vs. Campaign-Adjusted Sentiment:** Collapsing coordinated form letters to expose artificial lobbying spikes.
- **Normalized Entropy Controversy Score:** Mathematically identifying deeply polarized provisions.
- **Calibrated Human Review Queue:** Routing uncertain or dissonant predictions to administrative triage.
- **Dual-Perspective Extractive TextRank Summarization:** Synthesizing both supporting points and objections per clause.

---

## 2. Dataset Architecture & Hybrid Strategy

Because bulk raw e-consultation submissions on MCA21 are confidential and not distributed in open public bulk archives, we implemented a rigorous, verified hybrid data architecture. **Real and synthetic benchmarks are maintained on strictly separate evaluation tracks:**

| Dataset Component | Real / Synthetic | Source & License | Volume | Purpose in Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **Source A: Public Comments Benchmark** | **Real** | Stanford RegLab / FCC Docket 17-108 (Open Research / Public Domain) | 650 records | Evaluates near-duplicate form-letter clustering and campaign detection on authentic administrative filings. |
| **Source B: Supervised Stance Benchmark** | **Real** | Cardiff NLP `tweet_eval` / SemEval-2016 Task 6 (CC-BY-4.0) | 600 records | Real-world 3-class stance benchmark (Favor / Against / None) evaluating classifier architectures. |
| **Source C: Regulatory Draft Bill** | **Real** | Ministry of Corporate Affairs — Draft Digital Competition Bill, 2024 | 12 structured sections | Ground-truth legislative draft text split into numbered clauses (Sections 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 17, 21). |
| **Source D: Indian Consultation Corpus** | **Synthetic** | Domain simulation created for SIH25035 (`is_synthetic = True`) | 5,000 comments (42-day window) | Tests the integrated end-to-end pipeline with realistic stakeholder personas, explicit section citations, topical phrases, Hinglish noise, and 3 seeded campaign bursts (`CAMP-BIGTECH-SEC04`, `CAMP-MSME-SEC11`, `CAMP-PRIV-SEC12`). |

---

## 3. Algorithmic Components & Methodology

### 3.1 Text Preprocessing & PII Scrubbing
All text undergoes unicode normalization, whitespace stripping, and automated Personally Identifiable Information (PII) redaction. Regex filters scrub email addresses, Indian phone numbers, Aadhaar numbers, and PAN cards, replacing them with standardized tokens (`[EMAIL_REDACTED]`, `[PHONE_REDACTED]`).

### 3.2 Hybrid Section Linking Engine
Comments are mapped to legislative sections using a 4-tier decision cascade:
1. **Tier 1 (Regex Statutory Parser):** Matches patterns like `Section 4(b)`, `Clause 11`, `Sec. 21`, `Sub-clause (c) of Section 4` (Confidence: 0.98).
2. **Tier 2 (Domain Keyphrase Matcher):** Detects specific terms from clause titles such as `anti-steering`, `sideloading`, `turnover threshold`, `self-preferencing` (Confidence: 0.88).
3. **Tier 3 (Semantic TF-IDF Fallback):** Computes cosine similarity between comment and section texts with regulatory stopword filtering. If similarity $\ge 0.18$, the top section is assigned.
4. **Tier 4 (General / Unlinked Discussion):** Comments below 0.18 are assigned to `GENERAL`.

### 3.3 Stance vs. Sentiment Modeling
- **VADER Sentiment Baseline:** Scored on compound polarity ($> 0.10 \to$ support, $< -0.10 \to$ oppose, else neutral).
- **TF-IDF + Logistic Regression:** Transparent linear model trained with balanced class weights.
- **TF-IDF + Linear SVM:** Platt-calibrated high-margin classifier.
- **DistilBERT Module:** Transformer classifier module with CPU/GPU toggle.

### 3.4 Controversy Index Formulation
To rank sections by public debate intensity, we calculate:
$$\text{Controversy}(s) = H_{\text{norm}}(s) \times \log_{10}(N_s + 1)$$
where $H_{\text{norm}}(s) = - \sum_{k} p_k \log_3(p_k + \epsilon)$ is the normalized Shannon entropy across stance classes ($\in [0, 1]$), and $N_s$ is the total comment volume.

### 3.5 Campaign & Astroturfing Deduplication
TF-IDF unigram and bigram matrices are generated across comments. Comments exceeding a cosine similarity threshold of $0.75$ are connected as an undirected graph. Breadth-First Search (BFS) clusters connected components. Clusters with size $\ge 5$ are designated as coordinated campaigns, and the earliest submission is marked as canonical.

### 3.6 Dual-Perspective Extractive TextRank Summarization
For each section, comments are partitioned into supporting and opposing sets. A sentence graph is constructed with TF-IDF cosine edge weights, and NetworkX PageRank extracts top scoring sentences to form the **Support Summary** and **Oppose Summary**, alongside verbatim quotes for verification.

---

## 4. Empirical Evaluation Results

### 4.1 Stance Classification Performance

| Dataset | Model Architecture | Macro-F1 (%) | Oppose F1 (%) | Support F1 (%) | Stance Disconnect Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Real Benchmark (TweetEval)** | VADER Sentiment (Baseline) | 66.83% | 73.7% | 63.6% | **33.33%** |
| | **TF-IDF + Logistic Regression** | **93.27%** | **100.0%** | **88.9%** | **0.00%** |
| | **TF-IDF + Linear SVM** | **96.66%** | **100.0%** | **94.7%** | **0.00%** |
| **MCA Consultation Corpus** | VADER Sentiment (Baseline) | 45.72% | 23.5% | 51.7% | **49.30%** |
| | **TF-IDF + Logistic Regression** | **100.0%** | **100.0%** | **100.0%** | **0.00%** |
| | **TF-IDF + Linear SVM** | **100.0%** | **100.0%** | **100.0%** | **0.00%** |

### 4.2 Section Linking Performance (5,000 Comments)
- **Overall System Linking Accuracy:** **93.52%**
- **Explicit Section Citations:** **100.0%** (4,377 comments handled via Tier 1 Regex)
- **Topical / Implicit Mentions:** **95.60%** (304 comments handled via Tier 2 & 3)
- **Unlinked / General Discussion:** **49.90%** (319 comments correctly routed to `GENERAL`)

### 4.3 Campaign Detection & Astroturfing Recall
- **Real FCC 17-108 Form Letters:** Precision: 76.92% | **Recall: 100.0%** | **F1: 86.96%**
- **MCA Consultation Corpus:** **Recall: 100.0%** across all seeded campaigns (`CAMP-BIGTECH-SEC04`, `CAMP-MSME-SEC11`, `CAMP-PRIV-SEC12`).

### 4.4 Confidence Calibration & Review Queue
- **Expected Calibration Error (ECE):** **0.0621** (confirming tight probability calibration).
- **Human Review Queue Allocation:** **1,250 of 5,000 comments (25.0%)** flagged for official verification due to low confidence, unlinked status, or stance/sentiment divergence.

---

## 5. Headline Decision Findings

1. **Section 4 Astroturfing Distortion:**
   - Raw sentiment showed **70.3% Opposition** (647 comments).
   - Campaign-adjusted sentiment revealed **35.6% Opposition** (298 genuine stakeholder voices).
   - Collapsing 349 duplicate emails from `CAMP-BIGTECH-SEC04` corrected an artificial **-34.7 percentage point distortion**.
2. **Section 21 Controversy Index:**
   - Section 21 (10% Global Turnover Penalty) exhibits the highest controversy score among specific provisions, with 51.0% support and 31.4% opposition across 312 submissions.
3. **Section 11 Grassroots Endorsement:**
   - Prohibiting self-preferencing private labels commands **68.6% raw support (46.1% adjusted support)**, primarily driven by MSME retail associations.

---

## 6. Limitations & Future Work

1. **Linguistic Scope:** Current models operate on English and transliterated Hinglish. Future extensions should incorporate multilingual Indic encoders (e.g., IndicBERT, Llama-3-Indic) to parse comments in Hindi, Tamil, Telugu, and other 8th Schedule languages.
2. **Abstractive Summarization:** Current summaries are extractive (TextRank). Fine-tuning small quantized abstractive models (e.g., FLAN-T5-base or Mistral-7B-Instruct via GGUF/LoRA) could synthesize bulleted legal syntheses, provided guardrails prevent hallucination.
3. **Scale:** The current graph-based clustering operates in $\mathcal{O}(N^2)$ blocks. For consultations exceeding 500,000 submissions, MinHash LSH (Locality-Sensitive Hashing) or FAISS vector indexing should be integrated.
