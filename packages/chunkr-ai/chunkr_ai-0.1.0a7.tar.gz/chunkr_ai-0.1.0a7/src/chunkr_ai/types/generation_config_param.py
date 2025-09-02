# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["GenerationConfigParam"]


class GenerationConfigParam(TypedDict, total=False):
    crop_image: Optional[Literal["All", "Auto"]]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: Optional[bool]
    """Generate LLM descriptions for this segment"""

    extended_context: Optional[bool]
    """Use the full page image as context for LLM generation"""

    format: Optional[Literal["Html", "Markdown"]]
    """The format for the `content` field of a segment."""

    strategy: Optional[Literal["LLM", "Auto", "Ignore"]]
    """The strategy for generating the `content` field of a segment."""
