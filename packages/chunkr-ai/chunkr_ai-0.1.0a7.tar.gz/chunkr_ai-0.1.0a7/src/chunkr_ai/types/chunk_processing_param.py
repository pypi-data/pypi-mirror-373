# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["ChunkProcessingParam", "Tokenizer", "TokenizerEnum", "TokenizerString"]


class TokenizerEnum(TypedDict, total=False):
    enum: Required[
        Annotated[Literal["Word", "Cl100kBase", "XlmRobertaBase", "BertBaseUncased"], PropertyInfo(alias="Enum")]
    ]
    """Use one of the predefined tokenizer types"""


class TokenizerString(TypedDict, total=False):
    string: Required[Annotated[str, PropertyInfo(alias="String")]]
    """
    Use any Hugging Face tokenizer by specifying its model ID Examples:
    "Qwen/Qwen-tokenizer", "facebook/bart-large"
    """


Tokenizer: TypeAlias = Union[TokenizerEnum, TokenizerString]


class ChunkProcessingParam(TypedDict, total=False):
    ignore_headers_and_footers: Optional[bool]
    """DEPRECATED: use `segment_processing.ignore` instead"""

    target_length: int
    """The target number of words in each chunk.

    If 0, each chunk will contain a single segment.
    """

    tokenizer: Tokenizer
    """The tokenizer to use for the chunking process."""
