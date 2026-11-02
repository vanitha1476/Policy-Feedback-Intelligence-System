"""Stance and sentiment modeling package."""
__all__ = [
    "VaderBaseline",
    "SklearnStancePipeline",
    "DistilBertStanceClassifier",
    "STANCE_LABELS",
    "LABEL2ID",
    "ID2LABEL"
]

def __getattr__(name: str):
    if name in __all__:
        import src.models.stance_classifier as sc
        return getattr(sc, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
