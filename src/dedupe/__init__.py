"""Near-duplicate and campaign detection package."""
__all__ = ["CampaignDetector"]

def __getattr__(name: str):
    if name == "CampaignDetector":
        from src.dedupe.campaign_detector import CampaignDetector
        return CampaignDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
