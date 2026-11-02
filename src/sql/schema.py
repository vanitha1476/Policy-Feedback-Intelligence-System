"""
SQLite Database Schema & Analytical Views for Policy & Regulatory Feedback Intelligence System.
Stores draft sections, stakeholder comments, model inferences, campaign clusters, and summaries.
"""

SCHEMA_SQL = """
-- 1. Draft Sections Table
CREATE TABLE IF NOT EXISTS sections (
    section_id TEXT PRIMARY KEY,
    section_number TEXT NOT NULL,
    section_title TEXT NOT NULL,
    chapter TEXT NOT NULL,
    section_text TEXT NOT NULL,
    key_topics TEXT NOT NULL
);

-- 2. Stakeholder Comments Table
CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    clean_text TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    stakeholder_type TEXT NOT NULL,
    source TEXT NOT NULL,
    is_synthetic INTEGER NOT NULL DEFAULT 1,
    true_section_id TEXT,
    true_stance TEXT,
    is_campaign INTEGER NOT NULL DEFAULT 0,
    campaign_id TEXT,
    citation_style TEXT,
    has_hinglish INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (true_section_id) REFERENCES sections(section_id)
);

-- 3. Model Predictions & Inferences Table
CREATE TABLE IF NOT EXISTS predictions (
    comment_id TEXT PRIMARY KEY,
    pred_section_id TEXT,
    section_confidence REAL,
    pred_stance TEXT,
    stance_confidence REAL,
    vader_compound REAL,
    vader_sentiment TEXT,
    needs_review INTEGER DEFAULT 0,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(comment_id),
    FOREIGN KEY (pred_section_id) REFERENCES sections(section_id)
);

-- 4. Campaign & Astroturfing Clusters Table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    target_section_id TEXT,
    canonical_comment_id TEXT,
    total_submissions INTEGER NOT NULL DEFAULT 1,
    stance TEXT NOT NULL,
    FOREIGN KEY (target_section_id) REFERENCES sections(section_id),
    FOREIGN KEY (canonical_comment_id) REFERENCES comments(comment_id)
);

-- 5. Section Summaries Table (Extractive Dual-Perspective TextRank)
CREATE TABLE IF NOT EXISTS summaries (
    section_id TEXT PRIMARY KEY,
    support_summary TEXT,
    oppose_summary TEXT,
    representative_support_quotes TEXT,
    representative_oppose_quotes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(section_id)
);

-- 6. Keywords per Section and Stance
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id TEXT NOT NULL,
    stance TEXT NOT NULL,
    keyword TEXT NOT NULL,
    tfidf_score REAL NOT NULL,
    FOREIGN KEY (section_id) REFERENCES sections(section_id)
);

-- ============================================================================
-- ANALYTICAL VIEWS
-- ============================================================================

-- View 1: Raw Section Stance Distribution
DROP VIEW IF EXISTS v_section_stance_raw;
CREATE VIEW v_section_stance_raw AS
SELECT 
    c.true_section_id AS section_id,
    COALESCE(s.section_title, 'General / Unlinked Discussion') AS section_title,
    COUNT(c.comment_id) AS total_comments,
    SUM(CASE WHEN c.true_stance = 'support' THEN 1 ELSE 0 END) AS support_count,
    SUM(CASE WHEN c.true_stance = 'oppose' THEN 1 ELSE 0 END) AS oppose_count,
    SUM(CASE WHEN c.true_stance = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
    ROUND(100.0 * SUM(CASE WHEN c.true_stance = 'support' THEN 1 ELSE 0 END) / COUNT(c.comment_id), 2) AS support_pct,
    ROUND(100.0 * SUM(CASE WHEN c.true_stance = 'oppose' THEN 1 ELSE 0 END) / COUNT(c.comment_id), 2) AS oppose_pct,
    ROUND(100.0 * SUM(CASE WHEN c.true_stance = 'neutral' THEN 1 ELSE 0 END) / COUNT(c.comment_id), 2) AS neutral_pct
FROM comments c
LEFT JOIN sections s ON c.true_section_id = s.section_id
GROUP BY c.true_section_id;

-- View 2: Campaign-Adjusted Section Stance Distribution
-- Collapses all comments belonging to the same campaign into a single canonical submission
DROP VIEW IF EXISTS v_section_stance_adjusted;
CREATE VIEW v_section_stance_adjusted AS
WITH deduplicated_comments AS (
    -- Keep all organic comments
    SELECT comment_id, true_section_id, true_stance, is_campaign, campaign_id
    FROM comments
    WHERE is_campaign = 0
    
    UNION ALL
    
    -- Pick exactly 1 representative canonical comment per campaign
    SELECT MIN(comment_id) AS comment_id, true_section_id, true_stance, is_campaign, campaign_id
    FROM comments
    WHERE is_campaign = 1
    GROUP BY campaign_id, true_section_id, true_stance
)
SELECT 
    d.true_section_id AS section_id,
    COALESCE(s.section_title, 'General / Unlinked Discussion') AS section_title,
    COUNT(d.comment_id) AS adjusted_comments,
    SUM(CASE WHEN d.true_stance = 'support' THEN 1 ELSE 0 END) AS support_count,
    SUM(CASE WHEN d.true_stance = 'oppose' THEN 1 ELSE 0 END) AS oppose_count,
    SUM(CASE WHEN d.true_stance = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
    ROUND(100.0 * SUM(CASE WHEN d.true_stance = 'support' THEN 1 ELSE 0 END) / COUNT(d.comment_id), 2) AS support_pct,
    ROUND(100.0 * SUM(CASE WHEN d.true_stance = 'oppose' THEN 1 ELSE 0 END) / COUNT(d.comment_id), 2) AS oppose_pct,
    ROUND(100.0 * SUM(CASE WHEN d.true_stance = 'neutral' THEN 1 ELSE 0 END) / COUNT(d.comment_id), 2) AS neutral_pct
FROM deduplicated_comments d
LEFT JOIN sections s ON d.true_section_id = s.section_id
GROUP BY d.true_section_id;

-- View 3: Controversy Ranking (Entropy * Volume)
-- Compares polarization across sections
DROP VIEW IF EXISTS v_controversy_ranking;
CREATE VIEW v_controversy_ranking AS
SELECT 
    r.section_id,
    r.section_title,
    r.total_comments,
    r.support_pct,
    r.oppose_pct,
    r.neutral_pct,
    -- Normalized entropy calculation: higher when support, oppose, and neutral are evenly balanced
    ROUND(
        (
            - (CASE WHEN r.support_pct > 0 THEN (r.support_pct/100.0) * (ln(r.support_pct/100.0) / ln(3)) ELSE 0 END)
            - (CASE WHEN r.oppose_pct > 0 THEN (r.oppose_pct/100.0) * (ln(r.oppose_pct/100.0) / ln(3)) ELSE 0 END)
            - (CASE WHEN r.neutral_pct > 0 THEN (r.neutral_pct/100.0) * (ln(r.neutral_pct/100.0) / ln(3)) ELSE 0 END)
        ) * (ln(r.total_comments + 1) / ln(10)),
        4
    ) AS controversy_score
FROM v_section_stance_raw r
ORDER BY controversy_score DESC;

-- View 4: Weekly Stance Trend (Velocity over Time)
DROP VIEW IF EXISTS v_weekly_trends;
CREATE VIEW v_weekly_trends AS
SELECT 
    strftime('%Y-W%W', timestamp) AS consultation_week,
    true_section_id AS section_id,
    COUNT(comment_id) AS comment_count,
    SUM(CASE WHEN true_stance = 'support' THEN 1 ELSE 0 END) AS support_count,
    SUM(CASE WHEN true_stance = 'oppose' THEN 1 ELSE 0 END) AS oppose_count,
    SUM(CASE WHEN true_stance = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
    SUM(CASE WHEN is_campaign = 1 THEN 1 ELSE 0 END) AS campaign_count
FROM comments
GROUP BY strftime('%Y-W%W', timestamp), true_section_id;
"""
