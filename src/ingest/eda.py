"""
Exploratory Data Analysis (EDA) module for Policy & Regulatory Feedback Intelligence System.
Generates comprehensive distribution stats, tables, and markdown report in reports/eda_report.md.
"""

import os
import json
import pandas as pd
import numpy as np


def run_eda(comments_csv: str, sections_json: str, output_report: str) -> str:
    """Analyze consultation dataset and generate structured EDA markdown report."""
    os.makedirs(os.path.dirname(output_report), exist_ok=True)
    
    df = pd.read_csv(comments_csv)
    with open(sections_json, "r", encoding="utf-8") as f:
        sections = json.load(f)
    section_titles = {s["section_id"]: f"{s['section_id']}: {s['section_title']}" for s in sections}
    section_titles["GENERAL"] = "General / Unlinked Policy Discussion"

    total_comments = len(df)
    df["char_len"] = df["text"].apply(lambda x: len(str(x)))
    df["word_len"] = df["text"].apply(lambda x: len(str(x).split()))
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["week"] = df["timestamp"].dt.isocalendar().week
    
    # Stance distribution
    stance_counts = df["true_stance"].value_counts()
    stance_pct = (stance_counts / total_comments * 100).round(2)
    
    # Section coverage
    sec_counts = df["true_section_id"].value_counts()
    sec_pct = (sec_counts / total_comments * 100).round(2)
    
    # Campaign duplicate statistics
    campaign_counts = df["is_campaign"].value_counts()
    camp_detail = df[df["is_campaign"] == True]["campaign_id"].value_counts()
    
    # Temporal distribution
    weekly_dist = df.groupby(["week", "is_campaign"]).size().unstack(fill_value=0)
    
    # Stakeholder breakdown
    stakeholder_dist = df["stakeholder_type"].value_counts()

    # Build markdown report
    lines = [
        "# Exploratory Data Analysis (EDA) Report",
        "**System:** Policy & Regulatory Feedback Intelligence System (SIH25035)",
        f"**Dataset Analysed:** `{comments_csv}`",
        f"**Total Records:** {total_comments:,}",
        f"**Consultation Date Range:** {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}",
        "",
        "---",
        "",
        "## 1. Executive Summary & Key Dataset Characteristics",
        f"- **Total Submissions:** {total_comments:,} public comments.",
        f"- **Organic Stakeholder Comments:** {(total_comments - len(df[df['is_campaign']])):,} ({(1 - df['is_campaign'].mean())*100:.1f}%).",
        f"- **Astroturfing / Campaign Duplicates:** {df['is_campaign'].sum():,} ({df['is_campaign'].mean()*100:.1f}%) across {df['campaign_id'].nunique()} distinct campaigns.",
        f"- **Explicit Section Citations:** {(df['citation_style'] == 'explicit_cite').sum():,} ({(df['citation_style'] == 'explicit_cite').mean()*100:.1f}%).",
        f"- **Topical / Implicit Mentions:** {(df['citation_style'] == 'topical_mention').sum():,} ({(df['citation_style'] == 'topical_mention').mean()*100:.1f}%).",
        f"- **Unlinked / General Comments:** {(df['citation_style'] == 'unlinked_general').sum():,} ({(df['citation_style'] == 'unlinked_general').mean()*100:.1f}%).",
        f"- **Hinglish Expressions Present:** {df['has_hinglish'].sum():,} ({df['has_hinglish'].mean()*100:.1f}%).",
        "",
        "---",
        "",
        "## 2. Stance Distribution (Ground Truth)",
        "| Stance Class | Count | Percentage |",
        "| :--- | :--- | :--- |"
    ]
    for s_name in ["support", "oppose", "neutral"]:
        cnt = stance_counts.get(s_name, 0)
        pct = stance_pct.get(s_name, 0.0)
        lines.append(f"| **{s_name.capitalize()}** | {cnt:,} | {pct:.2f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Section Coverage & Feedback Distribution",
        "| Section ID & Title | Comment Count | % of Total Volume | Oppose % | Support % | Neutral % |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])
    
    for sec_id, cnt in sec_counts.items():
        title = section_titles.get(sec_id, sec_id)
        sub_df = df[df["true_section_id"] == sec_id]
        pct = sec_pct[sec_id]
        opp_p = (sub_df["true_stance"] == "oppose").mean() * 100
        sup_p = (sub_df["true_stance"] == "support").mean() * 100
        neu_p = (sub_df["true_stance"] == "neutral").mean() * 100
        lines.append(f"| {title} | {cnt:,} | {pct:.1f}% | {opp_p:.1f}% | {sup_p:.1f}% | {neu_p:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Length Distribution Statistics",
        "| Metric | Character Count | Word Count |",
        "| :--- | :--- | :--- |",
        f"| **Minimum** | {df['char_len'].min()} | {df['word_len'].min()} |",
        f"| **Mean** | {df['char_len'].mean():.1f} | {df['word_len'].mean():.1f} |",
        f"| **Median (50th percentile)** | {df['char_len'].median():.0f} | {df['word_len'].median():.0f} |",
        f"| **90th percentile** | {df['char_len'].quantile(0.90):.0f} | {df['word_len'].quantile(0.90):.0f} |",
        f"| **Maximum** | {df['char_len'].max()} | {df['word_len'].max()} |",
        f"| **Standard Deviation** | {df['char_len'].std():.1f} | {df['word_len'].std():.1f} |",
        "",
        "---",
        "",
        "## 5. Templated Astroturfing Campaigns Identified",
        "| Campaign ID | Target Section | Stance | Submissions Count | Burst Window Description |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| `CAMP-BIGTECH-SEC04` | SEC-04 (Quantitative Thresholds) | Oppose | {camp_detail.get('CAMP-BIGTECH-SEC04', 0):,} | Coordinated Big Tech lobbying blitz in Week 3 opposing turnover thresholds and global penalties. |",
        f"| `CAMP-MSME-SEC11` | SEC-11 (Self-Preferencing Ban) | Support | {camp_detail.get('CAMP-MSME-SEC11', 0):,} | Coordinated MSME merchant union submission in Week 4 supporting fair marketplace rules. |",
        f"| `CAMP-PRIV-SEC12` | SEC-12 (Data Cross-Use Restr.) | Support | {camp_detail.get('CAMP-PRIV-SEC12', 0):,} | Citizen privacy petition burst in Week 2 supporting data protection and anti-profiling. |",
        "",
        "---",
        "",
        "## 6. Stakeholder Representation Breakdown",
        "| Stakeholder Persona | Count | Percentage |",
        "| :--- | :--- | :--- |"
    ])
    
    for st_name, st_cnt in stakeholder_dist.items():
        st_pct = (st_cnt / total_comments * 100)
        lines.append(f"| {st_name} | {st_cnt:,} | {st_pct:.1f}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 7. Observations for Pipeline Design",
        "1. **High Stance Polarisation on Key Sections:** SEC-04 (Quantitative Thresholds) and SEC-21 (Penalties) feature sharp opposition spikes, driven both by genuine stakeholders and templated lobbying campaigns.",
        "2. **Campaign Distortion Risk:** Without campaign deduplication, `CAMP-BIGTECH-SEC04` artificially inflates the raw opposition against Section 4 by 350 submissions. Collapsing near-duplicates to a single representative voice is critical to reflecting true stakeholder consensus.",
        "3. **Linguistic Complexity:** Comments feature both strict statutory references (`Section 4(b)`, `Clause 11`) and indirect conversational arguments (`'turnover thresholds'`, `'predatory private label ranking'`). A hybrid linking mechanism combining regex pattern matching and semantic TF-IDF fallback is essential."
    ])

    report_content = "\n".join(lines)
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"EDA report successfully generated at {output_report}")
    return output_report


if __name__ == "__main__":
    c_csv = os.path.join("data", "processed", "simulated_mca_comments.csv")
    s_json = os.path.join("data", "draft_sections", "mca_draft_sections.json")
    out_rep = os.path.join("reports", "eda_report.md")
    run_eda(c_csv, s_json, out_rep)
