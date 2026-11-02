"""
Domain-Adapted Keyword and Keyphrase Mining Engine.
Extracts salient keywords per Section and per Stance with legal stopword filtering.
Populates SQLite keywords table for dashboard word clouds and thematic drill-down.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

from src.sql.db_manager import get_db_connection


DOMAIN_STOPWORDS = list(ENGLISH_STOP_WORDS) + [
    "section", "clause", "bill", "act", "provisions", "draft", "proposed",
    "government", "ministry", "mca", "competition", "digital", "india", "indian",
    "submission", "regarding", "reference", "enterprises", "enterprise", "services",
    "core", "business", "users", "dear", "sir", "madam", "sincerely", "respectfully"
]


def extract_keywords_per_section_stance(db_path: str = "data/consultation.db", top_k: int = 10) -> List[Dict[str, Any]]:
    """Mine top keywords per section and stance using TF-IDF."""
    conn = get_db_connection(db_path)
    comments_df = pd.read_sql_query("""
        SELECT true_section_id, true_stance, clean_text
        FROM comments
        WHERE clean_text IS NOT NULL AND clean_text != ''
    """, conn)
    
    cur = conn.cursor()
    cur.execute("DELETE FROM keywords") # Clean refresh
    
    results = []
    
    grouped = comments_df.groupby(["true_section_id", "true_stance"])
    
    for (sec_id, stance), group in grouped:
        texts = group["clean_text"].tolist()
        if not texts:
            continue
            
        vectorizer = TfidfVectorizer(
            stop_words=DOMAIN_STOPWORDS,
            ngram_range=(1, 2),
            max_features=50,
            sublinear_tf=True
        )
        try:
            tfidf_mat = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            mean_scores = tfidf_mat.mean(axis=0).A1
            
            top_indices = mean_scores.argsort()[::-1][:top_k]
            
            records_to_insert = []
            for idx in top_indices:
                kw = feature_names[idx]
                score = round(float(mean_scores[idx]), 4)
                records_to_insert.append((sec_id, stance, kw, score))
                results.append({
                    "section_id": sec_id,
                    "stance": stance,
                    "keyword": kw,
                    "score": score
                })
                
            cur.executemany("""
                INSERT INTO keywords (section_id, stance, keyword, tfidf_score)
                VALUES (?, ?, ?, ?)
            """, records_to_insert)
        except ValueError:
            continue
            
    conn.commit()
    conn.close()
    print(f"Extracted and saved {len(results)} keywords into {db_path}")
    return results


if __name__ == "__main__":
    extract_keywords_per_section_stance()
