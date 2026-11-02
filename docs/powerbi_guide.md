# Microsoft Power BI Integration Guide

**Project:** Policy & Regulatory Feedback Intelligence System  
**Problem Statement Reference:** SIH25035 (Ministry of Corporate Affairs)  
**Export Directory:** `powerbi_export/`  

---

## 1. Overview & Transparency Notice

> [!NOTE]
> **Engineering Disclosure:** AI agents and automated scripts cannot natively generate proprietary compiled binary `.pbix` files, as Microsoft Power BI Desktop utilizes a closed proprietary file archive specification. 
> Instead, our pipeline outputs pristine, pre-modeled, and schema-validated CSV files in `powerbi_export/`. This guide explains how officials and project evaluators can import these files into Power BI Desktop in under 3 minutes.

---

## 2. Exported Data Catalog (`powerbi_export/`)

| File Name | Schema Type | Key Fields | Purpose |
| :--- | :--- | :--- | :--- |
| **`sections.csv`** | Dimension Table | `section_id`, `section_number`, `section_title`, `chapter`, `section_text` | Legislative draft clause hierarchy |
| **`comments_predictions.csv`** | Fact Table | `comment_id`, `timestamp`, `stakeholder_type`, `true_section_id`, `pred_stance`, `stance_confidence`, `vader_sentiment`, `is_campaign`, `needs_review` | Granular comment-level records with ML inferences and review queue flags |
| **`section_stance_comparison.csv`** | Aggregate View | `section_id`, `section_title_raw`, `total_comments`, `adjusted_comments`, `oppose_pct_raw`, `oppose_pct_adj`, `volume_drop`, `oppose_delta` | Core headline comparison: Raw vs. Campaign-Adjusted sentiment |
| **`controversy_rankings.csv`** | Analytical Ranking | `section_id`, `section_title`, `total_comments`, `controversy_score`, `support_pct`, `oppose_pct`, `neutral_pct` | Polarization rankings based on Normalized Shannon Entropy |
| **`weekly_trends.csv`** | Time-Series Fact | `consultation_week`, `section_id`, `comment_count`, `support_count`, `oppose_count`, `campaign_count` | Submission velocity and weekly stance shifts |
| **`campaigns.csv`** | Cluster Dimension | `campaign_id`, `campaign_name`, `target_section_id`, `total_submissions`, `stance` | Coordinated astroturfing campaigns detected |

---

## 3. Step-by-Step Power BI Loading Instructions

### Step 1: Open Power BI Desktop
1. Launch **Microsoft Power BI Desktop**.
2. Click **Get Data** $\to$ **Text/CSV**.
3. Navigate to the `powerbi_export/` folder in your project repository.
4. Select `section_stance_comparison.csv` and click **Load**. Repeat for `comments_predictions.csv`, `sections.csv`, and `controversy_rankings.csv`.

### Step 2: Establish Model Relationships (Model View)
In the Power BI **Model View**, link the tables using standard star-schema relationships:
- Connect `sections.csv` (`section_id`) $\to$ `comments_predictions.csv` (`true_section_id`) *(One-to-Many)*.
- Connect `sections.csv` (`section_id`) $\to$ `section_stance_comparison.csv` (`section_id`) *(One-to-One)*.

### Step 3: Recommended Visualizations
1. **Raw vs. Adjusted Dissent Bar Chart:**
   - **X-axis:** `section_title`
   - **Y-axis:** `oppose_pct_raw` and `oppose_pct_adj` (Clustered Column Chart).
   - *Highlight:* Visualizes how Section 4 drops from 70% to 35% opposition once campaign duplicates are collapsed.
2. **Controversy Index Treemap:**
   - **Category:** `section_title`
   - **Values:** `controversy_score`
3. **Temporal Velocity Area Chart:**
   - **X-axis:** `consultation_week`
   - **Y-axis:** `comment_count`
   - **Legend:** `pred_stance`
4. **Administrative Review Queue Card:**
   - KPI card displaying total comments where `needs_review == 1`.
