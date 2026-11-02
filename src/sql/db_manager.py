"""
Database Manager for Policy & Regulatory Feedback Intelligence System.
Initializes SQLite database, registers custom math functions, loads sections & comments,
and executes analytical views.
"""

import os
import json
import sqlite3
import math
import pandas as pd
from typing import Optional

from src.sql.schema import SCHEMA_SQL


def get_db_connection(db_path: str = "data/consultation.db") -> sqlite3.Connection:
    """Create SQLite connection and register standard mathematical functions."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    # Register ln() math function for robust entropy calculations across all SQLite versions
    conn.create_function("ln", 1, lambda x: math.log(x) if x and x > 0 else 0.0)
    conn.create_function("log10", 1, lambda x: math.log10(x) if x and x > 0 else 0.0)
    return conn


def init_db(db_path: str = "data/consultation.db"):
    """Execute DDL script to create tables and views."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"Initialized database schema and views at {db_path}")


def populate_sections(sections_json: str, db_path: str = "data/consultation.db"):
    """Insert draft sections into the sections table."""
    with open(sections_json, "r", encoding="utf-8") as f:
        sections = json.load(f)
        
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    for s in sections:
        cursor.execute("""
            INSERT OR REPLACE INTO sections 
            (section_id, section_number, section_title, chapter, section_text, key_topics)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            s["section_id"],
            s["section_number"],
            s["section_title"],
            s["chapter"],
            s["section_text"],
            json.dumps(s.get("key_topics", []))
        ))
    
    conn.commit()
    conn.close()
    print(f"Successfully loaded {len(sections)} sections into {db_path}")


def populate_comments(comments_csv: str, db_path: str = "data/consultation.db"):
    """Insert consultation comments into the comments table."""
    df = pd.read_csv(comments_csv)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    records = []
    for _, row in df.iterrows():
        records.append((
            row["comment_id"],
            row["text"],
            row["clean_text"],
            row["timestamp"],
            row["stakeholder_type"],
            row["source"],
            1 if row["is_synthetic"] else 0,
            row["true_section_id"],
            row["true_stance"],
            1 if row["is_campaign"] else 0,
            row["campaign_id"] if pd.notna(row["campaign_id"]) else None,
            row["citation_style"],
            1 if row["has_hinglish"] else 0
        ))
        
    cursor.executemany("""
        INSERT OR REPLACE INTO comments 
        (comment_id, text, clean_text, timestamp, stakeholder_type, source,
         is_synthetic, true_section_id, true_stance, is_campaign, campaign_id,
         citation_style, has_hinglish)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    print(f"Successfully inserted {len(records)} comments into {db_path}")


def populate_campaign_metadata(db_path: str = "data/consultation.db"):
    """Populate campaigns table with cluster size and canonical IDs."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO campaigns (campaign_id, campaign_name, target_section_id, canonical_comment_id, total_submissions, stance)
        SELECT 
            campaign_id,
            CASE 
                WHEN campaign_id = 'CAMP-BIGTECH-SEC04' THEN 'Big Tech Lobby Anti-Threshold Campaign'
                WHEN campaign_id = 'CAMP-MSME-SEC11' THEN 'MSME Retail Coalition Pro-Fairness Campaign'
                WHEN campaign_id = 'CAMP-PRIV-SEC12' THEN 'Digital Rights Citizen Privacy Petition'
                ELSE campaign_id
            END AS campaign_name,
            true_section_id AS target_section_id,
            MIN(comment_id) AS canonical_comment_id,
            COUNT(comment_id) AS total_submissions,
            true_stance AS stance
        FROM comments
        WHERE is_campaign = 1 AND campaign_id IS NOT NULL
        GROUP BY campaign_id, true_section_id, true_stance
    """)
    
    conn.commit()
    conn.close()
    print(f"Populated campaign metadata in {db_path}")


def setup_database(db_path: str = "data/consultation.db",
                   sections_json: str = "data/draft_sections/mca_draft_sections.json",
                   comments_csv: str = "data/processed/simulated_mca_comments.csv"):
    """End-to-end database bootstrap function."""
    init_db(db_path)
    populate_sections(sections_json, db_path)
    populate_comments(comments_csv, db_path)
    populate_campaign_metadata(db_path)


if __name__ == "__main__":
    setup_database()
