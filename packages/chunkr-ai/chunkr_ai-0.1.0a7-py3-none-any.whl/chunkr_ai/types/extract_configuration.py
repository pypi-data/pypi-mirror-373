# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .parse_configuration import ParseConfiguration

__all__ = ["ExtractConfiguration"]


class ExtractConfiguration(BaseModel):
    schema_: object = FieldInfo(alias="schema")
    """The schema to be used for the extraction."""

    parse_configuration: Optional[ParseConfiguration] = None
    """
    Optional configuration for the `parse` task. Can not be used if `file` is a
    `task_id`.
    """

    system_prompt: Optional[str] = None
    """The system prompt to be used for the extraction."""
