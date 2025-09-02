# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["GenerationConfig"]


class GenerationConfig(BaseModel):
    crop_image: Optional[Literal["All", "Auto"]] = None
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: Optional[bool] = None
    """Generate LLM descriptions for this segment"""

    extended_context: Optional[bool] = None
    """Use the full page image as context for LLM generation"""

    format: Optional[Literal["Html", "Markdown"]] = None
    """The format for the `content` field of a segment."""

    strategy: Optional[Literal["LLM", "Auto", "Ignore"]] = None
    """The strategy for generating the `content` field of a segment."""
