"""Keyword mining package."""
__all__ = ["extract_keywords_per_section_stance", "DOMAIN_STOPWORDS"]

def __getattr__(name: str):
    if name in ("extract_keywords_per_section_stance", "DOMAIN_STOPWORDS"):
        from src.keywords.keyword_miner import extract_keywords_per_section_stance, DOMAIN_STOPWORDS
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
