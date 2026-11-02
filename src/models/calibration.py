"""
Confidence Calibration and Human Review Queue Router.
Computes Expected Calibration Error (ECE) and partitions predictions into:
- High-Confidence Automated Inferences
- Low-Confidence / High-Risk Human Review Queue
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple


def compute_ece(confidences: np.ndarray, accuracies: np.ndarray, n_bins: int = 10) -> Dict[str, Any]:
    """Calculate Expected Calibration Error (ECE) across confidence bins."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0.0
    bin_stats = []
    
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            bin_error = np.abs(avg_confidence_in_bin - accuracy_in_bin)
            ece += bin_error * prop_in_bin
            
            bin_stats.append({
                "bin_range": f"{bin_lower:.1f} - {bin_upper:.1f}",
                "count": int(np.sum(in_bin)),
                "avg_confidence": round(float(avg_confidence_in_bin), 4),
                "accuracy": round(float(accuracy_in_bin), 4),
                "gap": round(float(bin_error), 4)
            })
            
    return {
        "ece": round(float(ece), 4),
        "bins": bin_stats
    }


def evaluate_review_queue(df: pd.DataFrame, threshold: float = 0.55) -> Dict[str, Any]:
    """Partition predictions by threshold and evaluate high-confidence vs review queue accuracy."""
    y_true = df["true_stance"]
    y_pred = df["pred_stance"]
    confs = df["stance_confidence"]
    
    is_correct = (y_true == y_pred)
    
    high_conf_mask = (confs >= threshold)
    low_conf_mask = (confs < threshold)
    
    high_conf_acc = np.mean(is_correct[high_conf_mask]) if np.sum(high_conf_mask) > 0 else 0.0
    low_conf_acc = np.mean(is_correct[low_conf_mask]) if np.sum(low_conf_mask) > 0 else 0.0
    
    ece_results = compute_ece(confs.values, is_correct.values, n_bins=10)
    
    return {
        "threshold": threshold,
        "total_comments": len(df),
        "high_confidence_count": int(np.sum(high_conf_mask)),
        "high_confidence_pct": round(float(np.mean(high_conf_mask) * 100), 2),
        "high_confidence_accuracy": round(float(high_conf_acc * 100), 2),
        "review_queue_count": int(np.sum(low_conf_mask)),
        "review_queue_pct": round(float(np.mean(low_conf_mask) * 100), 2),
        "review_queue_accuracy": round(float(low_conf_acc * 100), 2),
        "ece": ece_results["ece"],
        "calibration_bins": ece_results["bins"]
    }
