"""
Calibrates and updates the Human Review Queue in SQLite.
Flags ambiguous predictions (lowest confidence quantile, unlinked sections, or stance/sentiment dissonance).
"""

import sqlite3
import pandas as pd
from src.sql.db_manager import get_db_connection


def update_review_queue(db_path: str = "data/consultation.db"):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    # Reset all to 0
    cur.execute("UPDATE predictions SET needs_review = 0")
    
    # Flag:
    # 1. Stance confidence < 0.88 (bottom confidence tier)
    # 2. General / unlinked comments requiring manual clause routing
    # 3. Severe stance vs sentiment divergence (e.g. negative words but predicted support) where confidence < 0.93
    cur.execute("""
        UPDATE predictions 
        SET needs_review = 1 
        WHERE stance_confidence < 0.88
           OR pred_section_id = 'GENERAL'
           OR (pred_stance != vader_sentiment AND stance_confidence < 0.93)
    """)
    
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM predictions WHERE needs_review = 1")
    queue_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM predictions")
    total_count = cur.fetchone()[0]
    
    print(f"Human Review Queue populated: {queue_count} of {total_count} comments ({queue_count/total_count*100:.1f}%) flagged for manual audit.")
    conn.close()
    return queue_count


if __name__ == "__main__":
    update_review_queue()
