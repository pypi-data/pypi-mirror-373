# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TaskGetParams"]


class TaskGetParams(TypedDict, total=False):
    base64_urls: bool
    """Whether to return base64 encoded URLs.

    If false, the URLs will be returned as presigned URLs.
    """

    include_chunks: bool
    """Whether to include chunks in the output response"""

    wait_for_completion: bool
    """Whether to wait for the task to complete"""
