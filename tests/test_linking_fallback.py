"""
Unit tests for the Hybrid Section Linker (Regex -> Keyphrase -> TF-IDF Fallback -> Unlinked).
"""

import pytest
from src.linking.section_linker import SectionLinker


@pytest.fixture(scope="module")
def linker():
    return SectionLinker(
        sections_json_path="data/draft_sections/mca_draft_sections.json",
        fallback_threshold=0.18
    )


def test_regex_linking_tier(linker):
    # Explicit statutory citations
    res1 = linker.link_comment("With reference to Section 4(b), the INR 4,000 crore turnover is excessive.")
    assert res1["section_id"] == "SEC-04"
    assert res1["strategy"] == "explicit_regex"
    assert res1["confidence"] >= 0.95

    res2 = linker.link_comment("Regarding Clause 11, marketplaces should not favor private labels.")
    assert res2["section_id"] == "SEC-11"
    assert res2["strategy"] == "explicit_regex"


def test_keyphrase_linking_tier(linker):
    # Topical mentions without citing section number
    res1 = linker.link_comment("We strongly condemn anti-steering rules that penalize developers for out-of-app purchases.")
    assert res1["section_id"] == "SEC-10"
    assert res1["strategy"] == "keyphrase_match"
    assert res1["confidence"] >= 0.85

    res2 = linker.link_comment("Forcing platforms to permit sideloading and alternative app stores creates security risks.")
    assert res2["section_id"] == "SEC-14"
    assert res2["strategy"] == "keyphrase_match"


def test_tfidf_fallback_tier(linker):
    # Mentions terms that semantically overlap with section text
    res = linker.link_comment("Imposing a 10 percent global turnover sanction is a disproportionate fine for procedural non-compliance.")
    assert res["section_id"] == "SEC-21"
    assert res["strategy"] in ["keyphrase_match", "semantic_tfidf_fallback"]


def test_unlinked_general_tier(linker):
    # Broad comment with no section-specific terminology
    res = linker.link_comment("The government must balance economic growth with ease of doing business in India.")
    assert res["section_id"] == "GENERAL"
    assert res["strategy"] == "unlinked_general"
