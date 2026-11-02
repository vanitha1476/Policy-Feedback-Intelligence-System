"""Extractive summarization package."""
__all__ = ["generate_section_summaries", "textrank_extract"]

def __getattr__(name: str):
    if name in ("generate_section_summaries", "textrank_extract"):
        from src.summarize.summarizer import generate_section_summaries, textrank_extract
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
