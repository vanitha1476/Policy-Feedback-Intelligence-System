"""Analytics and insight generation package."""
__all__ = ["generate_executive_insights"]

def __getattr__(name: str):
    if name == "generate_executive_insights":
        from src.analytics.insight_generator import generate_executive_insights
        return generate_executive_insights
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
