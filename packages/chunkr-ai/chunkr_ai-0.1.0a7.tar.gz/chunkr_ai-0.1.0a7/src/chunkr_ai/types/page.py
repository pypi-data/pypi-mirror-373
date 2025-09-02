# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Page"]


class Page(BaseModel):
    image: str
    """The presigned URL of the page/sheet image."""

    page_height: float
    """The number of pages in the file."""

    page_number: int
    """The number of pages in the file."""

    page_width: float
    """The number of pages in the file."""

    dpi: Optional[float] = None
    """DPI of the page/sheet. All cropped images are scaled to this DPI."""

    ss_sheet_name: Optional[str] = None
    """The name of the sheet containing the page. Only used for Spreadsheets."""
