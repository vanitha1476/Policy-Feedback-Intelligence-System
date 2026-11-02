# Viva Examination & Evaluation Notes

**Project Title:** Policy & Regulatory Feedback Intelligence System  
**Hackathon / Problem Reference:** Smart India Hackathon 2025 (Problem Statement: SIH25035)  
**Client / Ministry:** Ministry of Corporate Affairs (MoCA), Government of India  
**Target Legal Draft:** Draft Digital Competition Bill, 2024 (CDCL Draft Rules)  

---

## 1. What is the Core Novelty of this Project?

> [!IMPORTANT]
> **Be Honest with Examiners:** Sentiment analysis itself is not new. If you tell an examiner "we built sentiment analysis", they will say it is trivial. 
> **Your Real Contribution:** The domain-adapted **Decision-Support System** designed specifically for legislative e-consultation:
> 1. **Clause-Level Aggregation:** Moving beyond broad document sentiment to section-by-section analysis ("Where does opposition concentrate?").
> 2. **Astroturfing & Campaign Deduplication:** Identifying near-duplicate form-letter campaigns that artificially distort democratic consensus.
> 3. **The Stance vs. Sentiment Disconnect:** Proving empirically that standard sentiment tools fail on ~49% of regulatory comments, requiring dedicated 3-class stance classification.
> 4. **Controversy Index Formulation:** Combining normalized Shannon entropy with volume to rank disputed sections.
> 5. **Trust-but-Verify (Calibrated Review Queue):** Routing low-confidence and conflicting predictions to human officials for auditable review.

---

## 2. Model Architecture Trade-Offs

| Dimension | Lexical VADER | TF-IDF + Logistic Regression | Fine-Tuned DistilBERT | Generative LLMs (e.g. GPT/Llama) |
| :--- | :--- | :--- | :--- | :--- |
| **Macro-F1 on Stance** | 45.7% (Fails on disconnect) | **93.3% - 98.2%** | 99.1% | High |
| **Inference Latency** | < 0.1 ms | **< 0.5 ms (CPU)** | ~ 24 ms (GPU needed) | 500 - 2,000 ms |
| **Hardware Cost** | Zero | **Zero (Runs on any laptop)** | High (GPU server) | Very High (API / Cloud) |
| **Explainability** | Dictionary rules | **Complete (Feature weights)** | Low (Attention weights) | Black-box / Hallucination risk |
| **Court / Committee Audit** | Inadmissible | **Auditable feature table** | Difficult | Risky |

---

## 3. 15 Likely Viva Questions & Model Answers

### Q1: What is the objective of SIH25035 and who is the ministry?
**Answer:** The Ministry of Corporate Affairs (MCA) receives thousands of comments on draft rules (via the MCA21 e-Consultation module). Officials cannot read them all. Our system automatically links comments to draft sections, classifies stance, collapses coordinated duplicate campaigns, calculates controversy scores, and provides decision-ready summaries for policymakers.

---

### Q2: Why is Stance Detection different from Sentiment Analysis? Give a real example.
**Answer:** Sentiment measures emotional tone (positive/negative), while Stance measures agreement with a specific proposition (Support/Oppose/Neutral). In policy feedback, stakeholders frequently use harsh, angry words (*"predatory monopolies", "draconian market power", "crush startups"*) to strongly **SUPPORT** strict regulatory intervention. Standard sentiment tools like VADER misclassify ~49% of policy comments because of this disconnect.

---

### Q3: How did you handle the lack of open Indian e-consultation datasets?
**Answer:** We implemented a verified hybrid data strategy:
1. Real external benchmark from FCC Docket 17-108 net neutrality comments for campaign deduplication.
2. Real benchmark from SemEval-2016 / TweetEval for stance detection.
3. Authentic text and 12 sections from the MCA Draft Digital Competition Bill, 2024.
4. A simulated dataset of 5,000 comments across a 6-week window with realistic personas and seeded campaign bursts, strictly labeled with `is_synthetic: True` and evaluated on separate tracks.

---

### Q4: What is astroturfing in public consultations and why is it dangerous?
**Answer:** Astroturfing is the practice of interest groups, corporations, or bots submitting hundreds of slight variations of a pre-written form letter. If 350 duplicate emails oppose a section, an official looking at raw counts might believe 70% of citizens reject the bill. Collapsing duplicates to 1 representative voice reveals that genuine grassroots opposition is only ~35%.

---

### Q5: How does your Near-Duplicate & Campaign Detection algorithm work?
**Answer:** We compute unigram and bigram TF-IDF representations for each comment and calculate pairwise cosine similarity. Comments exceeding a calibrated threshold of $0.75$ form edges in a graph. Using Breadth-First Search (BFS) connected components, clusters with $\ge 5$ comments are designated as coordinated campaigns. The earliest comment is marked as the canonical version, and duplicates are collapsed for campaign-adjusted metrics.

---

### Q6: How does the Section Linking Engine handle comments that do not mention a section number?
**Answer:** We use a 4-tier hybrid pipeline:
1. Regex matches explicit statutory cites (`Section 4(b)`, `Clause 11`).
2. If absent, Keyphrase Matcher scans for specific clause concepts (`anti-steering`, `sideloading`).
3. If absent, TF-IDF cosine similarity compares the comment against section clause texts with regulatory stopword pruning.
4. If similarity is below $0.18$, it is routed to `GENERAL` (Unlinked Discussion).

---

### Q7: What is the Controversy Score and how is it calculated mathematically?
**Answer:** It measures both polarization and public participation volume:
$$\text{Controversy}(s) = H_{\text{norm}}(s) \times \log_{10}(N_s + 1)$$
where $H_{\text{norm}}(s)$ is the normalized Shannon entropy across the 3 stance classes ($\in [0, 1]$), which peaks when opinions are evenly split (e.g. 50/50 support/oppose), and $N_s$ is the total submission count.

---

### Q8: Why did you prioritize Linear Models (TF-IDF + Logistic Regression/SVM) over heavy LLMs?
**Answer:** For public policy governance, three factors are critical:
1. **Explainability:** Linear models expose exact coefficient weights (`indian` +1.83, `will` +1.74) that can be audited by parliamentary committees.
2. **Speed & Zero Cost:** Sub-millisecond CPU inference allows deployment on standard government intranet hardware without GPU infrastructure.
3. **Accuracy:** With balanced class weights, linear models achieved top-tier Macro-F1.

---

### Q9: What is Expected Calibration Error (ECE) and why does it matter?
**Answer:** ECE measures how well a model's predicted confidence corresponds to its true empirical accuracy. If a model predicts 80% confidence, it should be correct 80% of the time. Our model achieved an ECE of **0.0621**, confirming that confidence scores can be trusted to route uncertain predictions to human review.

---

### Q10: How does the Human Review Queue work?
**Answer:** To ensure "Trust-but-Verify", predictions with low confidence ($< 0.88$), unlinked sections, or where lexical sentiment contradicts policy stance are flagged (`needs_review = 1`). In our dataset, 1,250 comments (25%) are routed to the dashboard review queue where officials can inspect and manually adjudicate them.

---

### Q11: How do your summaries avoid bias toward one viewpoint?
**Answer:** We implemented **Dual-Perspective Extractive TextRank**: for each section, we partition comments into supporting and opposing sets and run sentence-level PageRank on each subset independently. The dashboard displays the top support arguments and top objections in parallel cards, paired with verbatim evidence quotes.

---

### Q12: How does the system handle Hinglish or noisy comments?
**Answer:** The preprocessing layer scrubs PII and normalizes unicode and whitespaces. Transliterated Hinglish terms (e.g., *"bahut cumbersome"*, *"desi startups"*) are treated as n-gram tokens by the TF-IDF vectorizer, enabling the models to learn their correlation with support or opposition without failing.

---

### Q13: What was the headline finding on Section 4 of the MCA Draft Digital Competition Bill?
**Answer:** Section 4 (Quantitative Thresholds) showed **70.3% raw opposition** across 647 submissions. After collapsing 349 duplicate emails from `CAMP-BIGTECH-SEC04`, the campaign-adjusted opposition dropped to **35.6%**, exposing a **34.7 percentage point artificial lobbying distortion**.

---

### Q14: Can this system integrate with Microsoft Power BI?
**Answer:** Yes. Our pipeline exports 6 relational, schema-validated CSV files in `powerbi_export/` (`sections.csv`, `comments_predictions.csv`, `section_stance_comparison.csv`, etc.). Officials can import these directly into Power BI Desktop in under 3 minutes following `docs/powerbi_guide.md`.

---

### Q15: What are the main limitations and future directions of this work?
**Answer:**
1. **Language Scope:** Currently handles English and light Hinglish; future work should incorporate IndicBERT and multilingual embeddings for Hindi, Tamil, and other regional languages.
2. **Abstractive Summarization:** Current summaries are extractive; fine-tuning a small, guardrailed LLM (e.g., FLAN-T5-base) could produce synthesized legal bullet points.
3. **Scale:** Current clustering is $\mathcal{O}(N^2)$ in batches; for consultations exceeding 500,000 comments, MinHash LSH or FAISS vector indexing should be used.
