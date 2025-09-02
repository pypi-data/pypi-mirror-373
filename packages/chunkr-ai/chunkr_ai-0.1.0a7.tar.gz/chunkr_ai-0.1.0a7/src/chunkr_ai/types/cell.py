# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .cell_style import CellStyle

__all__ = ["Cell"]


class Cell(BaseModel):
    cell_id: str
    """The cell ID."""

    range: str
    """Range of the cell."""

    text: str
    """Text content of the cell."""

    formula: Optional[str] = None
    """Formula of the cell."""

    hyperlink: Optional[str] = None
    """Hyperlink URL if the cell contains a link (e.g., "https://www.chunkr.ai")."""

    style: Optional[CellStyle] = None
    """Styling information for the cell including colors, fonts, and formatting."""

    value: Optional[str] = None
    """The computed/evaluated value of the cell.

    This represents the actual result after evaluating any formulas, as opposed to
    the raw text content. For cells with formulas, this is the calculated result;
    for cells with static content, this is typically the same as the text field.

    Example: text might show "3.14" (formatted to 2 decimal places) while value
    could be "3.141592653589793" (full precision).
    """
