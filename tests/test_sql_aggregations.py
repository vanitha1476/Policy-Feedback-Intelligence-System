"""
Unit tests for SQLite database schema, views, and raw vs. campaign-adjusted aggregations.
"""

import pytest
import sqlite3
import pandas as pd
from src.sql.db_manager import get_db_connection, setup_database


@pytest.fixture(scope="module")
def test_db():
    db_file = "data/consultation.db"
    # Ensure database is set up
    setup_database(db_file)
    conn = get_db_connection(db_file)
    yield conn
    conn.close()


def test_tables_populated(test_db):
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM sections")
    sec_count = cursor.fetchone()[0]
    assert sec_count == 12

    cursor.execute("SELECT COUNT(*) FROM comments")
    com_count = cursor.fetchone()[0]
    assert com_count == 5000

    cursor.execute("SELECT COUNT(*) FROM campaigns")
    camp_count = cursor.fetchone()[0]
    assert camp_count == 3


def test_raw_vs_adjusted_delta(test_db):
    # SEC-04 has CAMP-BIGTECH-SEC04 (350 submissions collapsed to 1)
    df_raw = pd.read_sql_query("SELECT * FROM v_section_stance_raw WHERE section_id = 'SEC-04'", test_db)
    df_adj = pd.read_sql_query("SELECT * FROM v_section_stance_adjusted WHERE section_id = 'SEC-04'", test_db)
    
    assert len(df_raw) == 1
    assert len(df_adj) == 1
    
    raw_total = df_raw["total_comments"].iloc[0]
    adj_total = df_adj["adjusted_comments"].iloc[0]
    
    # 350 campaign comments collapsed to 1 means a delta of 349
    assert raw_total - adj_total == 349
    
    # Raw opposition percentage should be higher than campaign-adjusted opposition
    assert df_raw["oppose_pct"].iloc[0] > df_adj["oppose_pct"].iloc[0]


def test_controversy_ranking_view(test_db):
    df_controversy = pd.read_sql_query("SELECT * FROM v_controversy_ranking", test_db)
    assert len(df_controversy) > 0
    # Controversy scores must be non-null and positive
    assert (df_controversy["controversy_score"] > 0).all()
    # Top section should have highest controversy score
    assert df_controversy["controversy_score"].iloc[0] >= df_controversy["controversy_score"].iloc[-1]
