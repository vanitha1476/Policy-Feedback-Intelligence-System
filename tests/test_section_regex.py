"""
Unit tests for rule-based section citation regex extraction.
"""

import pytest
import re

# Section extraction regex matching patterns like "Section 4(b)", "Clause 11", "Sec. 3", "Section 12"
SECTION_REGEX = re.compile(
    r'(?:section|clause|sec\.?)\s+([0-9]{1,2}(?:\([a-z0-9]+\))?)',
    re.IGNORECASE
)

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


def extract_section_citation(text: str):
    match = SECTION_REGEX.search(text)
    if not match:
        return None
    raw_num = match.group(1).lower()
    base_num = re.sub(r'\(.*?\)', '', raw_num).strip()
    return SECTION_MAP.get(base_num)


def test_explicit_section_cites():
    assert extract_section_citation("In reference to Section 4(b), the threshold is high.") == "SEC-04"
    assert extract_section_citation("Clause 11 prohibits self preferencing.") == "SEC-11"
    assert extract_section_citation("Under Sec. 21, the penalty is 10%.") == "SEC-21"
    assert extract_section_citation("Regarding section 3 of the draft bill") == "SEC-03"
    assert extract_section_citation("Clause 10(1) restricts anti-steering") == "SEC-10"


def test_no_section_citation():
    assert extract_section_citation("This bill needs more consultation with industry.") is None
    assert extract_section_citation("Competition in digital markets is good.") is None
