"""
Hybrid Section Linking Engine for Legislative & Regulatory Consultations.

Hierarchy:
1. Rule-Based Regex: Explicit statutory section/clause citations (Confidence: 0.95 - 1.0)
2. Domain Keyphrase Matcher: High-specificity regulatory terms from clause titles (Confidence: 0.80 - 0.90)
3. Semantic TF-IDF Fallback: Cosine similarity between comment and section text (Confidence: Cosine Score)
4. General / Unlinked Bucket: Assigned when similarity falls below calibrated threshold (Default: 0.12)
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SECTION_MAP = {
    "3": "SEC-03",
    "4": "SEC-04",
    "5": "SEC-05",
    "6": "SEC-06",
    "7": "SEC-07",
    "10": "SEC-10",
    "11": "SEC-11",
    "12": "SEC-12",
    "13": "SEC-13",
    "14": "SEC-14",
    "17": "SEC-17",
    "21": "SEC-21"
}

# Regex to match "Section 4(b)", "Clause 11", "Sec. 21", "sub-clause (c) of section 4"
SECTION_REGEX = re.compile(
    r'(?:(?:sub-clause\s*\([a-z0-9]+\)\s*of\s*)?(?:section|clause|sec\.?))\s+([0-9]{1,2}(?:\([a-z0-9]+\))?)',
    re.IGNORECASE
)


class SectionLinker:
    def __init__(self, sections_json_path: str = "data/draft_sections/mca_draft_sections.json",
                 fallback_threshold: float = 0.18):
        self.fallback_threshold = fallback_threshold
        with open(sections_json_path, "r", encoding="utf-8") as f:
            self.sections = json.load(f)
            
        self.section_ids = [s["section_id"] for s in self.sections]
        self.section_map_by_id = {s["section_id"]: s for s in self.sections}
        
        # Build domain keyphrase mappings
        self._build_keyphrase_index()
        
        # Build TF-IDF semantic index
        self._build_tfidf_index()

    def _build_keyphrase_index(self):
        """Map highly specific regulatory keyphrases to target section IDs."""
        self.keyphrase_rules = {
            "SEC-03": ["designation of ssde", "core digital service", "designate an enterprise", "criteria for designation"],
            "SEC-04": ["quantitative threshold", "turnover threshold", "4,000 crore", "4000 crore", "30 billion", "gross merchandise value", "gmv", "user threshold", "business users"],
            "SEC-05": ["qualitative criteria", "qualitative factor", "network effects", "switching costs", "user lock-in", "vertical integration"],
            "SEC-06": ["associate enterprises", "group entities", "subsidiaries", "holding company", "corporate groups"],
            "SEC-07": ["code of fair conduct", "fair dealing", "merchant termination", "arbitrary termination", "algorithmic ranking"],
            "SEC-10": ["anti-steering", "anti steering", "external links", "out-of-app", "commission fee", "app store commission"],
            "SEC-11": ["self-preferencing", "self preferencing", "private labels", "search bias", "ranking manipulation", "marketplace neutrality"],
            "SEC-12": ["data cross-use", "cross-use", "merchant data", "confidential commercial data", "user profiling", "profiling"],
            "SEC-13": ["interoperability", "open standards", "technical interoperability", "open apis", "ecosystem lock-in"],
            "SEC-14": ["sideloading", "side-loading", "third-party application stores", "alternative app stores", "default apps", "in-app payments"],
            "SEC-17": ["dispute redressal", "dispute resolution", "compliance officer", "15 days", "15-day dispute", "grievance redressal"],
            "SEC-21": ["10% global turnover", "10 percent", "global turnover penalty", "penalties for contravention", "divestment", "draconian penalty"]
        }

    def _build_tfidf_index(self):
        """Fit TF-IDF vectorizer over rich section documents with regulatory stopwords."""
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        custom_stopwords = list(ENGLISH_STOP_WORDS) + [
            "india", "business", "enterprise", "enterprises", "services", "digital",
            "core", "act", "bill", "provisions", "commission", "government", "shall"
        ]
        corpus = []
        for s in self.sections:
            doc = f"{s['section_title']} {s['section_text']} {' '.join(s.get('key_topics', []))}"
            corpus.append(doc)
            
        self.tfidf_vectorizer = TfidfVectorizer(stop_words=custom_stopwords, ngram_range=(1, 2))
        self.section_matrix = self.tfidf_vectorizer.fit_transform(corpus)

    def extract_regex_citation(self, text: str) -> Optional[str]:
        """Tier 1: Explicit statutory regex matching."""
        match = SECTION_REGEX.search(text)
        if not match:
            return None
        raw_num = match.group(1).lower()
        base_num = re.sub(r'\(.*?\)', '', raw_num).strip()
        return SECTION_MAP.get(base_num)

    def match_keyphrase(self, text: str) -> Optional[str]:
        """Tier 2: High-precision domain keyphrase matching."""
        lower_text = text.lower()
        for sec_id, phrases in self.keyphrase_rules.items():
            for phrase in phrases:
                if phrase in lower_text:
                    return sec_id
        return None

    def link_comment(self, text: str) -> Dict[str, Any]:
        """Link a single comment to its relevant draft section with confidence and strategy."""
        if not text or not isinstance(text, str):
            return {
                "section_id": "GENERAL",
                "confidence": 0.0,
                "strategy": "empty_input",
                "section_title": "General / Unlinked Discussion"
            }

        # Tier 1: Explicit Citation
        regex_sec = self.extract_regex_citation(text)
        if regex_sec and regex_sec in self.section_map_by_id:
            return {
                "section_id": regex_sec,
                "confidence": 0.98,
                "strategy": "explicit_regex",
                "section_title": self.section_map_by_id[regex_sec]["section_title"]
            }

        # Tier 2: Domain Keyphrase Match
        keyphrase_sec = self.match_keyphrase(text)
        if keyphrase_sec and keyphrase_sec in self.section_map_by_id:
            return {
                "section_id": keyphrase_sec,
                "confidence": 0.88,
                "strategy": "keyphrase_match",
                "section_title": self.section_map_by_id[keyphrase_sec]["section_title"]
            }

        # Tier 3: TF-IDF Cosine Similarity Fallback
        comment_vec = self.tfidf_vectorizer.transform([text])
        similarities = cosine_similarity(comment_vec, self.section_matrix)[0]
        best_idx = int(np.argmax(similarities))
        best_sim = float(similarities[best_idx])

        if best_sim >= self.fallback_threshold:
            sec_id = self.section_ids[best_idx]
            return {
                "section_id": sec_id,
                "confidence": round(best_sim, 4),
                "strategy": "semantic_tfidf_fallback",
                "section_title": self.section_map_by_id[sec_id]["section_title"]
            }

        # Tier 4: General / Unlinked Discussion
        return {
            "section_id": "GENERAL",
            "confidence": round(1.0 - best_sim, 4),
            "strategy": "unlinked_general",
            "section_title": "General / Unlinked Policy Discussion"
        }

    def link_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch processing of comments."""
        return [self.link_comment(t) for t in texts]
