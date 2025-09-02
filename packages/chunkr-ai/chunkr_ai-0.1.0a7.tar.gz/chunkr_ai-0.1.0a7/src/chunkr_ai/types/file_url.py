# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["FileURL"]


class FileURL(BaseModel):
    url: str
    """The presigned URL or base64 data (if base64_urls=true)"""

    expires_in: Optional[int] = None
    """Expiry in seconds (omitted when base64)"""
