"""
Dual-Perspective Extractive TextRank Summarization Engine.
Produces explainable, balanced summaries preserving both:
- Core Supporting Arguments
- Major Objections / Opposition Concerns
Plus verbatim representative stakeholder quotes as empirical evidence.
"""

import os
import json
import sqlite3
import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

from src.sql.db_manager import get_db_connection


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences, filtering short fragments."""
    # Split on period, exclamation, question mark followed by space or end
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned = []
    for s in raw_sentences:
        s = s.strip()
        if len(s) > 25 and len(s.split()) >= 4:
            cleaned.append(s)
    return cleaned


def textrank_extract(sentences: List[str], top_k: int = 3) -> List[str]:
    """Graph-based PageRank / TextRank over sentence similarity matrix."""
    if not sentences:
        return []
    if len(sentences) <= top_k:
        return sentences

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_mat = vectorizer.fit_transform(sentences)
    except ValueError:
        return sentences[:top_k]

    sim_mat = cosine_similarity(tfidf_mat, tfidf_mat)
    # Set diagonal to zero to avoid self-loops
    np.fill_diagonal(sim_mat, 0.0)

    # Build networkx graph
    nx_graph = nx.from_numpy_array(sim_mat)
    try:
        scores = nx.pagerank(nx_graph, max_iter=200, tol=1e-4)
    except Exception:
        scores = {i: float(np.sum(sim_mat[i])) for i in range(len(sentences))}

    ranked_indices = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)
    top_indices = sorted(ranked_indices[:top_k])
    return [sentences[i] for i in top_indices]


def generate_section_summaries(db_path: str = "data/consultation.db", top_k: int = 2) -> Dict[str, Any]:
    """Generate dual-perspective summaries and store in SQLite summaries table."""
    conn = get_db_connection(db_path)
    
    # Query all sections
    sections_df = pd.read_sql_query("SELECT section_id, section_title FROM sections", conn)
    comments_df = pd.read_sql_query("""
        SELECT c.comment_id, c.text, c.clean_text, c.true_section_id, c.true_stance, c.stakeholder_type
        FROM comments c
    """, conn)
    
    cur = conn.cursor()
    summaries_dict = {}

    for _, sec in sections_df.iterrows():
        sec_id = sec["section_id"]
        sec_title = sec["section_title"]
        sec_comments = comments_df[comments_df["true_section_id"] == sec_id]
        
        # Support comments
        sup_comments = sec_comments[sec_comments["true_stance"] == "support"]
        sup_texts = sup_comments["clean_text"].dropna().tolist()
        sup_sentences = []
        for t in sup_texts:
            sup_sentences.extend(split_into_sentences(t))
        # Deduplicate sentences while preserving order
        sup_sentences = list(dict.fromkeys(sup_sentences))
        support_summary_list = textrank_extract(sup_sentences, top_k=top_k)
        support_summary = " ".join(support_summary_list) if support_summary_list else "No significant supporting comments received."
        rep_support_quotes = json.dumps(sup_texts[:3] if len(sup_texts) >= 3 else sup_texts)

        # Oppose comments
        opp_comments = sec_comments[sec_comments["true_stance"] == "oppose"]
        opp_texts = opp_comments["clean_text"].dropna().tolist()
        opp_sentences = []
        for t in opp_texts:
            opp_sentences.extend(split_into_sentences(t))
        opp_sentences = list(dict.fromkeys(opp_sentences))
        oppose_summary_list = textrank_extract(opp_sentences, top_k=top_k)
        oppose_summary = " ".join(oppose_summary_list) if oppose_summary_list else "No significant opposition comments received."
        rep_oppose_quotes = json.dumps(opp_texts[:3] if len(opp_texts) >= 3 else opp_texts)

        summaries_dict[sec_id] = {
            "section_title": sec_title,
            "support_summary": support_summary,
            "oppose_summary": oppose_summary,
            "representative_support_quotes": json.loads(rep_support_quotes),
            "representative_oppose_quotes": json.loads(rep_oppose_quotes)
        }

        # Store in database
        cur.execute("""
            INSERT OR REPLACE INTO summaries 
            (section_id, support_summary, oppose_summary, representative_support_quotes, representative_oppose_quotes)
            VALUES (?, ?, ?, ?, ?)
        """, (sec_id, support_summary, oppose_summary, rep_support_quotes, rep_oppose_quotes))

    conn.commit()
    conn.close()
    print(f"Generated and saved dual-perspective summaries for {len(summaries_dict)} sections to {db_path}")
    return summaries_dict


if __name__ == "__main__":
    generate_section_summaries()
