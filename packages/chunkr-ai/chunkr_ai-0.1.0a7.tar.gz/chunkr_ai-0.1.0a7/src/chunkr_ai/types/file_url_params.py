# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FileURLParams"]


class FileURLParams(TypedDict, total=False):
    base64_urls: bool
    """If true, returns base64 data instead of a presigned URL"""

    expires_in: int
    """Expiry in seconds for the presigned URL (default 3600)"""
