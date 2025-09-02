# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel
from .llm_processing import LlmProcessing
from .chunk_processing import ChunkProcessing
from .segment_processing import SegmentProcessing

__all__ = ["ParseConfiguration"]


class ParseConfiguration(BaseModel):
    chunk_processing: Optional[ChunkProcessing] = None
    """Controls the setting for the chunking and post-processing of each chunk."""

    error_handling: Optional[Literal["Fail", "Continue"]] = None
    """Controls how errors are handled during processing:

    - `Fail`: Stops processing and fails the task when any error occurs
    - `Continue`: Attempts to continue processing despite non-critical errors (eg.
      LLM refusals etc.)
    """

    llm_processing: Optional[LlmProcessing] = None
    """Controls the LLM used for the task."""

    ocr_strategy: Optional[Literal["All", "Auto"]] = None
    """Controls the Optical Character Recognition (OCR) strategy.

    - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
    - `Auto`: Selectively applies OCR only to pages with missing or low-quality
      text. When text layer is present the bounding boxes from the text layer are
      used.
    """

    pipeline: Optional[Literal["Azure", "Chunkr"]] = None

    segment_processing: Optional[SegmentProcessing] = None
    """Configuration for how each document segment is processed and formatted.

    Each segment has sensible defaults, but you can override specific settings:

    - `format`: Output as `Html` or `Markdown`
    - `strategy`: `Auto` (rule-based), `LLM` (AI-generated), or `Ignore` (skip)
    - `crop_image`: Whether to crop images to segment bounds
    - `extended_context`: Use full page as context for LLM processing
    - `description`: Generate descriptions for segments

    **Defaults per segment type:** Check the documentation for more details.

    Only specify the fields you want to change - everything else uses the defaults.
    """

    segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] = None
    """Controls the segmentation strategy:

    - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
      `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
      segmentation and better chunking.
    - `Page`: Treats each page as a single segment. Faster processing, but without
      layout element detection and only simple chunking.
    """
