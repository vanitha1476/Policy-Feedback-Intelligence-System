# Data Sources Log

**Project:** Policy & Regulatory Feedback Intelligence System  
**Reference:** SIH25035 (Ministry of Corporate Affairs)  
**Maintained by:** Senior NLP & Data Engineering Team  

Every data source used in this system is logged below with verification of availability, terms of use, license, and designated purpose.

---

## 1. Source A: Real Public Comment Corpus (Campaign & Duplicate Benchmark)
- **Source Name:** Stanford RegLab / FCC Docket 17-108 ("Restoring Internet Freedom") Public Comments
- **Identifier:** `slnader/fcc-comments` (Hugging Face) / FCC ECFS Public Docket 17-108
- **URL:** https://huggingface.co/datasets/slnader/fcc-comments
- **License / Terms of Use:** Public Domain / Open Research (US Government Open Public Record / CC-BY 4.0 research adaptation)
- **Date Verified:** 2026-10-13
- **Sampling Strategy:** Manageable random sample of comments (5,000–10,000 comments) containing verified duplicate submission batches.
- **Pipeline Role:** Serves as a real-world external benchmark for near-duplicate identification, cosine similarity clustering, and mass form-letter campaign detection.

---

## 2. Source B: Supervised Stance Benchmark Corpus
- **Source Name:** Cardiff NLP `tweet_eval` Stance Detection Benchmark (SemEval-2016 Task 6 adaptation)
- **Identifier:** `cardiffnlp/tweet_eval` (configs: `stance_climate`, `stance_feminist`, `stance_abortion`, `stance_atheism`)
- **URL:** https://huggingface.co/datasets/cardiffnlp/tweet_eval
- **License / Terms of Use:** Creative Commons Attribution 4.0 International (CC-BY-4.0)
- **Date Verified:** 2026-10-13
- **Size / Splits:** Standard train (~2,914), validation, and test splits across distinct policy targets.
- **Labels:** 0: `none` (neutral), 1: `against` (oppose), 2: `favor` (support).
- **Pipeline Role:** Provides an open, verified real-world ground truth benchmark for evaluating VADER baseline vs. TF-IDF Linear Models vs. fine-tuned DistilBERT on standard 3-class stance prediction.

---

## 3. Source C: Authentic Draft Document (Sections Table)
- **Source Name:** Ministry of Corporate Affairs (MCA) — Draft Digital Competition Bill, 2024 (Report of the Committee on Digital Competition Law)
- **Identifier:** `MCA-CDCL-2024-Draft`
- **URL:** https://www.mca.gov.in / Gazette of India Public Consultation
- **License / Terms of Use:** Public Legal Consultation Document / Open Government Publication
- **Date Verified:** 2026-10-13
- **Structure:** 12 numbered sections extracted into structured records (`section_id`, `section_number`, `title`, `full_text`, `key_topics`):
  - Section 3: Criteria for Designation of Systemically Significant Digital Enterprises (SSDEs)
  - Section 4: Quantitative Thresholds (Turnover, Market Capitalisation, User Base)
  - Section 5: Qualitative Criteria for SSDE Designation
  - Section 6: Associate Enterprises and Group Entities
  - Section 7: Obligations of SSDEs (General Conduct)
  - Section 10: Anti-Steering Provisions
  - Section 11: Self-Preferencing and Search Manipulation
  - Section 12: Data Usage, Cross-Use and User Consent
  - Section 13: Interoperability Requirements
  - Section 14: Restricting Third-Party Application Installations & Sideloading
  - Section 17: Dispute Resolution and Appellate Mechanism
  - Section 21: Penalties and Remedies for Non-Compliance
- **Pipeline Role:** Acts as the official draft legislation against which feedback is linked, analyzed, and summarized.

---

## 4. Source D: Simulated Indian e-Consultation Corpus
- **Source Name:** Indian e-Consultation MCA Stakeholder Feedback Simulation
- **Identifier:** `synthetic_mca_consultation_v1`
- **License / Terms of Use:** Created for this project (Apache 2.0 / MIT)
- **Date Generated:** 2026-10-13
- **Volume:** 5,000 comments across a realistic 6-week public consultation window.
- **Features Included:**
  - Explicit clause citations (e.g., `"Under Section 4(b)..."`, `"Clause 11 needs revision"`)
  - Topical implicit mentions (referring to "turnover thresholds", "anti-steering", "self-preferencing" without clause numbers)
  - General / unlinked policy feedback
  - Multi-stakeholder personas: Big Tech lobbies, Indian startup founders, MSME associations, legal scholars, citizen advocacy groups, anonymous citizens
  - Realistic linguistic noise (light Hinglish colloquialisms such as `"compliance bahut cumbersome hoga"`, typos, sarcastic tone)
  - Orchestrated duplicate campaigns: Seeded templated campaigns with near-identical wording (e.g., Campaign Alpha: 350 duplicate anti-Section 4 submissions; Campaign Beta: 200 duplicate pro-Section 11 submissions)
  - Timestamp patterns with a surge/burst during Week 3 & 4
  - Explicit metadata: `comment_id`, `text`, `timestamp`, `source`, `is_synthetic: True`, `true_section`, `true_stance`, `is_campaign`, `campaign_id`
- **Pipeline Role:** Tests the complete integrated pipeline (section linking, raw vs. adjusted stance delta, controversy score, weekly velocity, review queue).
