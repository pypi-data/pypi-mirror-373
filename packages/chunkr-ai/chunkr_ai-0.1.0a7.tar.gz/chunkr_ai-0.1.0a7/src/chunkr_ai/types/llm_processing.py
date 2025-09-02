# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["LlmProcessing", "FallbackStrategy", "FallbackStrategyModel"]


class FallbackStrategyModel(BaseModel):
    model: str = FieldInfo(alias="Model")
    """Use a specific model as fallback"""


FallbackStrategy: TypeAlias = Union[Literal["None", "Default"], FallbackStrategyModel]


class LlmProcessing(BaseModel):
    fallback_strategy: Optional[FallbackStrategy] = None
    """The fallback strategy to use for the LLMs in the task."""

    llm_model_id: Optional[str] = None
    """The ID of the model to use for the task.

    If not provided, the default model will be used. Please check the documentation
    for the model you want to use.
    """

    max_completion_tokens: Optional[int] = None
    """The maximum number of tokens to generate."""

    temperature: Optional[float] = None
    """The temperature to use for the LLM."""
