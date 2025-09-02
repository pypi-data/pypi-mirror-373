# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["LlmProcessingParam", "FallbackStrategy", "FallbackStrategyModel"]


class FallbackStrategyModel(TypedDict, total=False):
    model: Required[Annotated[str, PropertyInfo(alias="Model")]]
    """Use a specific model as fallback"""


FallbackStrategy: TypeAlias = Union[Literal["None", "Default"], FallbackStrategyModel]


class LlmProcessingParam(TypedDict, total=False):
    fallback_strategy: FallbackStrategy
    """The fallback strategy to use for the LLMs in the task."""

    llm_model_id: Optional[str]
    """The ID of the model to use for the task.

    If not provided, the default model will be used. Please check the documentation
    for the model you want to use.
    """

    max_completion_tokens: Optional[int]
    """The maximum number of tokens to generate."""

    temperature: float
    """The temperature to use for the LLM."""
