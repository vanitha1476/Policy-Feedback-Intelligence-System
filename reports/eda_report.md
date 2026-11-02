# Exploratory Data Analysis (EDA) Report
**System:** Policy & Regulatory Feedback Intelligence System (SIH25035)
**Dataset Analysed:** `data\processed\simulated_mca_comments.csv`
**Total Records:** 5,000
**Consultation Date Range:** 2024-03-01 to 2024-04-11

---

## 1. Executive Summary & Key Dataset Characteristics
- **Total Submissions:** 5,000 public comments.
- **Organic Stakeholder Comments:**  4250 (85.0%).
- **Astroturfing / Campaign Duplicates:** 750 (15.0%) across 3 distinct campaigns.
- **Explicit Section Citations:** 2,819 (56.4%).
- **Topical / Implicit Mentions:** 1,682 (33.6%).
- **Unlinked / General Comments:** 499 (10.0%).
- **Hinglish Expressions Present:** 314 (6.3%).

---

## 2. Stance Distribution (Ground Truth)
| Stance Class | Count | Percentage |
| :--- | :--- | :--- |
| **Support** | 2,306 | 46.12% |
| **Oppose** | 1,934 | 38.68% |
| **Neutral** | 760 | 15.20% |

---

## 3. Section Coverage & Feedback Distribution
| Section ID & Title | Comment Count | % of Total Volume | Oppose % | Support % | Neutral % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SEC-04: Quantitative Thresholds for SSDE Designation | 647 | 12.9% | 70.3% | 21.0% | 8.7% |
| SEC-11: Prohibition on Self-Preferencing and Search Bias | 596 | 11.9% | 23.8% | 68.6% | 7.6% |
| General / Unlinked Policy Discussion | 499 | 10.0% | 36.1% | 41.5% | 22.4% |
| SEC-12: Restrictions on Data Cross-Use, Profiling and Merchant Data Exploitation | 473 | 9.5% | 25.8% | 60.7% | 13.5% |
| SEC-07: General Obligations and Code of Fair Conduct | 327 | 6.5% | 38.2% | 43.4% | 18.3% |
| SEC-17: Dedicated Dispute Redressal and Compliance Officer | 324 | 6.5% | 37.0% | 45.4% | 17.6% |
| SEC-14: Allowing Third-Party Application Stores and Direct Sideloading | 312 | 6.2% | 38.8% | 43.9% | 17.3% |
| SEC-21: Penalties for Contravention of Ex-Ante Obligations | 312 | 6.2% | 31.4% | 51.0% | 17.6% |
| SEC-10: Prohibition on Anti-Steering Restrictions | 305 | 6.1% | 37.7% | 45.2% | 17.0% |
| SEC-03: Criteria for Designation of Systemically Significant Digital Enterprises (SSDEs) | 305 | 6.1% | 36.4% | 48.2% | 15.4% |
| SEC-13: Interoperability Requirements for Core Digital Platforms | 303 | 6.1% | 39.6% | 43.6% | 16.8% |
| SEC-05: Qualitative Factors for Determining Systemic Significance | 301 | 6.0% | 39.5% | 42.9% | 17.6% |
| SEC-06: Obligations of Associate Enterprises and Corporate Groups | 296 | 5.9% | 35.8% | 45.9% | 18.2% |

---

## 4. Length Distribution Statistics
| Metric | Character Count | Word Count |
| :--- | :--- | :--- |
| **Minimum** | 103 | 12 |
| **Mean** | 176.2 | 24.2 |
| **Median (50th percentile)** | 163 | 23 |
| **90th percentile** | 259 | 36 |
| **Maximum** | 378 | 55 |
| **Standard Deviation** | 54.5 | 7.7 |

---

## 5. Templated Astroturfing Campaigns Identified
| Campaign ID | Target Section | Stance | Submissions Count | Burst Window Description |
| :--- | :--- | :--- | :--- | :--- |
| `CAMP-BIGTECH-SEC04` | SEC-04 (Quantitative Thresholds) | Oppose | 350 | Coordinated Big Tech lobbying blitz in Week 3 opposing turnover thresholds and global penalties. |
| `CAMP-MSME-SEC11` | SEC-11 (Self-Preferencing Ban) | Support | 250 | Coordinated MSME merchant union submission in Week 4 supporting fair marketplace rules. |
| `CAMP-PRIV-SEC12` | SEC-12 (Data Cross-Use Restr.) | Support | 150 | Citizen privacy petition burst in Week 2 supporting data protection and anti-profiling. |

---

## 6. Stakeholder Representation Breakdown
| Stakeholder Persona | Count | Percentage |
| :--- | :--- | :--- |
| Tech Startup Founder | 629 | 12.6% |
| Individual Citizen | 622 | 12.4% |
| Legal Scholar / Law Firm | 621 | 12.4% |
| Anonymous | 597 | 11.9% |
| Consumer Advocate | 597 | 11.9% |
| Big Tech Corporate | 592 | 11.8% |
| MSME Retailer | 592 | 11.8% |
| Big Tech Lobby / Industry Association | 350 | 7.0% |
| MSME Retailers Association | 250 | 5.0% |
| Digital Rights & Consumer Coalition | 150 | 3.0% |

---

## 7. Observations for Pipeline Design
1. **High Stance Polarisation on Key Sections:** SEC-04 (Quantitative Thresholds) and SEC-21 (Penalties) feature sharp opposition spikes, driven both by genuine stakeholders and templated lobbying campaigns.
2. **Campaign Distortion Risk:** Without campaign deduplication, `CAMP-BIGTECH-SEC04` artificially inflates the raw opposition against Section 4 by 350 submissions. Collapsing near-duplicates to a single representative voice is critical to reflecting true stakeholder consensus.
3. **Linguistic Complexity:** Comments feature both strict statutory references (`Section 4(b)`, `Clause 11`) and indirect conversational arguments (`'turnover thresholds'`, `'predatory private label ranking'`). A hybrid linking mechanism combining regex pattern matching and semantic TF-IDF fallback is essential.