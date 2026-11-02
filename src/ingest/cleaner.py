"""
Text cleaning, PII anonymization, and normalization utilities.
Ensures zero personal data retention and uniform text representation.
"""

import re
import unicodedata
from typing import Dict, Any


EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_PATTERN = re.compile(r'(?:\+91[\s-]?)?[6789]\d{9}\b')
AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
WHITESPACE_PATTERN = re.compile(r'\s+')


def scrub_pii(text: str) -> str:
    """Scrub Personally Identifiable Information (Emails, Indian Phones, PAN, Aadhaar)."""
    if not text:
        return ""
    text = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    text = PHONE_PATTERN.sub("[PHONE_REDACTED]", text)
    text = AADHAAR_PATTERN.sub("[ID_REDACTED]", text)
    text = PAN_PATTERN.sub("[PAN_REDACTED]", text)
    return text


def normalize_text(text: str, remove_urls: bool = False) -> str:
    """Normalize unicode, whitespace, and scrub PII."""
    if not text or not isinstance(text, str):
        return ""
    
    # Unicode NFKD normalization
    text = unicodedata.normalize("NFKD", text)
    
    # Scrub PII
    text = scrub_pii(text)
    
    # Optional URL redaction
    if remove_urls:
        text = URL_PATTERN.sub("[LINK]", text)
        
    # Normalize whitespaces and linebreaks
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def is_valid_comment(text: str, min_chars: int = 15) -> bool:
    """Check if comment meets minimum substantive length threshold."""
    if not text or not isinstance(text, str):
        return False
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text)
    return len(cleaned) >= min_chars
