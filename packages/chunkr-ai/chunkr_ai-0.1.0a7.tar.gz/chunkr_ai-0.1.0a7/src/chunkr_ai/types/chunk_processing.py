# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ChunkProcessing", "Tokenizer", "TokenizerEnum", "TokenizerString"]


class TokenizerEnum(BaseModel):
    enum: Literal["Word", "Cl100kBase", "XlmRobertaBase", "BertBaseUncased"] = FieldInfo(alias="Enum")
    """Use one of the predefined tokenizer types"""


class TokenizerString(BaseModel):
    string: str = FieldInfo(alias="String")
    """
    Use any Hugging Face tokenizer by specifying its model ID Examples:
    "Qwen/Qwen-tokenizer", "facebook/bart-large"
    """


Tokenizer: TypeAlias = Union[TokenizerEnum, TokenizerString]


class ChunkProcessing(BaseModel):
    ignore_headers_and_footers: Optional[bool] = None
    """DEPRECATED: use `segment_processing.ignore` instead"""

    target_length: Optional[int] = None
    """The target number of words in each chunk.

    If 0, each chunk will contain a single segment.
    """

    tokenizer: Optional[Tokenizer] = None
    """The tokenizer to use for the chunking process."""
