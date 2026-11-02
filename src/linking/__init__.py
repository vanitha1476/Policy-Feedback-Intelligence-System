"""Section linking module."""
__all__ = ["SectionLinker"]

def __getattr__(name: str):
    if name == "SectionLinker":
        from src.linking.section_linker import SectionLinker
        return SectionLinker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
