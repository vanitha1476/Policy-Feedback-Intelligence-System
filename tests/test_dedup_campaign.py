"""
Unit tests for duplicate and campaign detection logic.
"""

import pytest
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def test_near_duplicate_cosine_similarity():
    # Two variations of a seeded astroturfing template
    text_1 = "We strongly urge the Ministry to reconsider the arbitrary quantitative thresholds under Section 4 and penalties under Section 21."
    text_2 = "We respectfully submit that the arbitrary quantitative thresholds under Section 4 and penalties under Section 21 require urgent reconsideration."
    unrelated = "Section 14 sideloading requirements will introduce severe malware vulnerabilities into mobile smartphones."

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 1))
    tfidf_matrix = vectorizer.fit_transform([text_1, text_2, unrelated])
    
    sim_duplicates = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    sim_unrelated = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[2:3])[0][0]
    
    # Near duplicates share significantly higher cosine similarity than unrelated comments
    assert sim_duplicates > 0.45
    assert sim_unrelated < 0.10
