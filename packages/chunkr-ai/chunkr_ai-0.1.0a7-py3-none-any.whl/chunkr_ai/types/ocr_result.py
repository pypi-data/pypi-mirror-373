# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .bounding_box import BoundingBox

__all__ = ["OcrResult"]


class OcrResult(BaseModel):
    bbox: BoundingBox
    """Bounding box for an item. It is used for segments and OCR results."""

    text: str
    """The recognized text of the OCR result."""

    cell_ref: Optional[str] = None
    """
    Excel-style cell reference (e.g., "A1" or "A1:B2") when OCR originates from a
    spreadsheet cell
    """

    confidence: Optional[float] = None
    """The confidence score of the recognized text."""

    ocr_id: Optional[str] = None
    """The unique identifier for the OCR result."""
