# Project Assumptions & Domain Principles

**Project:** Policy & Regulatory Feedback Intelligence System  
**Reference:** SIH25035 (Ministry of Corporate Affairs)  
**Author:** Senior NLP & Data Engineering Team  

---

## 1. Domain & Theoretical Assumptions

### 1.1 Stance vs. Sentiment Disconnect
- **Assumption:** In public legislative consultations, **Stance** (whether a stakeholder supports, opposes, or remains neutral toward a proposed clause) is fundamentally distinct from **Sentiment** (lexical/emotional polarity).
- **Practical Implication:** A citizen or startup founder may use intense, angry, or alarmist words ("predatory practices", "unfair dominance", "chokehold on startups") to strongly **SUPPORT** an aggressive anti-monopoly clause (e.g., Section 11: Anti-Self-Preferencing). Conversely, polite, corporate phrasing may completely **OPPOSE** the section. 
- **System Design:** We compute both VADER sentiment (baseline) and a dedicated 3-class Stance model (`support`, `oppose`, `neutral`), tracking and reporting the divergence rate.

### 1.2 Campaign Duplication & Astroturfing
- **Assumption:** Public consultation windows are susceptible to orchestrated campaigns where interest groups, lobby coalitions, or automated bots submit hundreds of slight variations of a pre-written form letter.
- **Practical Implication:** Raw submission tallies give a distorted impression of democratic consensus. If 400 identical emails oppose Section 4, reporting "85% of citizens oppose Section 4" is misleading.
- **System Design:** We calculate metrics twice: **Raw** vs. **Campaign-Adjusted** (where clusters of near-duplicate submissions are collapsed to 1 canonical voice per campaign), demonstrating the true grassroots sentiment.

### 1.3 Controversy Index Definition
- **Assumption:** A section is "controversial" when public opinion is evenly divided across opposing stances and has substantial comment volume.
- **Mathematical Formulation:**
  $$\text{Controversy}(s) = H_{\text{norm}}(s) \times \log_{10}(N_s + 1)$$
  where $H_{\text{norm}}(s) = -\sum_{k} p_k \log_3(p_k + \epsilon)$ is the normalized Shannon entropy across the 3 stance classes ($\in [0, 1]$), and $N_s$ is the total comment volume on section $s$. A 50/50 support/oppose section ranks much higher in controversy than a 95% oppose section.

### 1.4 Trust-but-Verify (Uncertainty & Review Queue)
- **Assumption:** Automated NLP models in regulatory governance must never be black boxes that dictate policy unchecked.
- **System Design:** Every prediction is paired with a confidence score. Predictions below the calibrated threshold (default $\le 0.55$) are routed to an administrative **Human Review Queue** in the dashboard.

---

## 2. Data Strategy Assumptions

### 2.1 Hybrid Data Strategy
- **Reality:** While the Ministry of Corporate Affairs publishes draft bills and white papers, bulk raw stakeholder submissions submitted through the MCA21 e-Consultation module are not distributed as public bulk datasets due to confidentiality and privacy constraints.
- **Assumption & Solution:** We adopt a hybrid data strategy:
  1. **Real External Data (Source A & B):** We utilize public, open-access public comment data (Stanford/FCC 17-108 net neutrality docket) for real-world campaign/duplicate evaluation, and TweetEval/SemEval-2016 for real-world stance classification benchmarks.
  2. **Real Draft Document (Source C):** We use the authentic text and clause structure of the **Ministry of Corporate Affairs Draft Digital Competition Bill (CDCL 2024)**.
  3. **Simulated Consultation Data (Source D):** We generate realistic stakeholder comments (corporates, MSMEs, startups, civil society, legal practitioners) with explicit section citations, implicit topical phrases, unlinked general thoughts, Hinglish noise, and seeded campaign clusters.

### 2.2 Synthetic Integrity
- Every synthetic record has `is_synthetic: True`, ground truth labels (`true_section`, `true_stance`, `is_campaign`, `campaign_id`).
- Real and synthetic datasets are evaluated strictly on separate tracks; no metrics are merged or obfuscated.

### 2.3 Privacy & PII Handling
- Any real or simulated comments undergo PII normalization (scrubbing names, email addresses, phone numbers, and physical addresses) prior to database persistence.
