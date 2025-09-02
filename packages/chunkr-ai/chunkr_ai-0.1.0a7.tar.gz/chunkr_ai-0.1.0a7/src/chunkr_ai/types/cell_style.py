# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["CellStyle"]


class CellStyle(BaseModel):
    align: Optional[Literal["Left", "Center", "Right", "Justify"]] = None
    """Alignment of the cell content."""

    bg_color: Optional[str] = None
    """Background color of the cell (e.g., "#FFFFFF" or "#DAE3F3")."""

    font_face: Optional[str] = None
    """Font face/family of the cell (e.g., "Arial", "Daytona")."""

    is_bold: Optional[bool] = None
    """Whether the cell content is bold."""

    text_color: Optional[str] = None
    """Text color of the cell (e.g., "#000000" or "red")."""

    valign: Optional[Literal["Top", "Middle", "Bottom", "Baseline"]] = None
    """Vertical alignment of the cell content."""
