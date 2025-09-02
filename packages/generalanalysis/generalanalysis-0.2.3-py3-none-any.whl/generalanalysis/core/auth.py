"""Authentication handling for the General Analysis SDK."""

import os
from typing import Optional


def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Get API key from parameter or environment variable."""
    if api_key:
        return api_key

    # Check environment variable
    return os.environ.get("GA_API_KEY")


def get_base_url(base_url: Optional[str] = None) -> str:
    """Get base URL from parameter or use default."""
    if base_url:
        return base_url.rstrip("/")

    # Use production URL
    return "https://redit-api-dev.generalanalysis.com"
