"""
Evaluation module for Section Linking Engine.
Computes accuracy, citation-style breakdown, ablation study, and generates
the unverified human audit template in eval/section_link_manual_check.csv.
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score

from src.linking.section_linker import SectionLinker


def evaluate_linking_pipeline(comments_csv: str = "data/processed/simulated_mca_comments.csv",
                              sections_json: str = "data/draft_sections/mca_draft_sections.json",
                              output_sample_csv: str = "eval/section_link_manual_check.csv") -> Dict[str, Any]:
    os.makedirs(os.path.dirname(output_sample_csv), exist_ok=True)
    df = pd.read_csv(comments_csv)
    linker = SectionLinker(sections_json_path=sections_json, fallback_threshold=0.18)

    # Run predictions
    results = linker.link_batch(df["clean_text"].tolist())
    df["pred_section_id"] = [r["section_id"] for r in results]
    df["pred_strategy"] = [r["strategy"] for r in results]
    df["link_confidence"] = [r["confidence"] for r in results]

    y_true = df["true_section_id"]
    y_pred = df["pred_section_id"]

    overall_acc = accuracy_score(y_true, y_pred)
    
    # Accuracy by citation style
    style_acc = {}
    for style, group in df.groupby("citation_style"):
        style_acc[style] = round(accuracy_score(group["true_section_id"], group["pred_section_id"]) * 100, 2)

    # Strategy breakdown
    strategy_counts = df["pred_strategy"].value_counts().to_dict()

    print(f"Overall Linking Accuracy: {overall_acc * 100:.2f}%")
    print(f"Accuracy by citation style: {style_acc}")
    print(f"Predictions by strategy tier: {strategy_counts}")

    # Create unverified 120-comment manual audit sample file
    # Stratified sample across strategies and sections
    sample_dfs = []
    for _, grp in df.groupby("pred_strategy"):
        sample_dfs.append(grp.sample(min(len(grp), 30), random_state=42))
    sample_df = pd.concat(sample_dfs).sample(n=120, random_state=42)

    audit_export = pd.DataFrame({
        "comment_id": sample_df["comment_id"],
        "text": sample_df["text"],
        "predicted_section_id": sample_df["pred_section_id"],
        "predicted_strategy": sample_df["pred_strategy"],
        "link_confidence": sample_df["link_confidence"],
        "human_verified_section": "",  # To be filled by human auditor
        "human_decision": "",          # Agree / Disagree (To be filled by human)
        "auditor_notes": ""            # Remarks (To be filled by human)
    })

    audit_export.to_csv(output_sample_csv, index=False, encoding="utf-8")
    print(f"Saved 120-comment unverified audit template to {output_sample_csv}")

    return {
        "overall_accuracy": round(overall_acc * 100, 2),
        "style_accuracy": style_acc,
        "strategy_distribution": strategy_counts
    }


if __name__ == "__main__":
    evaluate_linking_pipeline()
