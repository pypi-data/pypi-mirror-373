# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ..parse_configuration_param import ParseConfigurationParam

__all__ = ["ExtractCreateParams"]


class ExtractCreateParams(TypedDict, total=False):
    file: Required[str]
    """The file to be extracted. Supported inputs:

    - `ch://files/{file_id}`: Reference to an existing file. Upload via the Files
      API
    - `http(s)://...`: Remote URL to fetch
    - `data:*;base64,...` or raw base64 string
    - `task_id`: Reference to an existing `parse`task.
    """

    schema: Required[object]
    """The schema to be used for the extraction."""

    expires_in: Optional[int]
    """
    The number of seconds until task is deleted. Expired tasks can **not** be
    updated, polled or accessed via web interface.
    """

    file_name: Optional[str]
    """The name of the file to be extracted.

    If not set a name will be generated. Can not be provided if the `file` is a
    `task_id`.
    """

    parse_configuration: Optional[ParseConfigurationParam]
    """
    Optional configuration for the `parse` task. Can not be used if `file` is a
    `task_id`.
    """

    system_prompt: Optional[str]
    """The system prompt to be used for the extraction."""
