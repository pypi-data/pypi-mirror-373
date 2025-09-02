# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .file_info import FileInfo
from .version_info import VersionInfo
from .parse_configuration import ParseConfiguration
from .extract_configuration import ExtractConfiguration
from .parse_output_response import ParseOutputResponse
from .extract_output_response import ExtractOutputResponse

__all__ = ["TaskResponse", "Configuration", "Output"]

Configuration: TypeAlias = Union[ParseConfiguration, ExtractConfiguration]

Output: TypeAlias = Union[ParseOutputResponse, ExtractOutputResponse, None]


class TaskResponse(BaseModel):
    configuration: Configuration
    """
    Unified configuration type that can represent either parse or extract
    configurations
    """

    created_at: datetime
    """The date and time when the task was created and queued."""

    file_info: FileInfo
    """Information about the input file."""

    message: str
    """A message describing the task's status or any errors that occurred."""

    status: Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]
    """The status of the task."""

    task_id: str
    """The unique identifier for the task."""

    task_type: Literal["Parse", "Extract"]

    version_info: VersionInfo
    """Version information for the task."""

    expires_at: Optional[datetime] = None
    """The date and time when the task will expire."""

    finished_at: Optional[datetime] = None
    """The date and time when the task was finished."""

    input_file_url: Optional[str] = None
    """The presigned URL of the input file. Deprecated use `file_info.url` instead."""

    output: Optional[Output] = None
    """Unified output type that can represent either parse or extract results"""

    source_task_id: Optional[str] = None
    """The ID of the source task that was used for the task"""

    started_at: Optional[datetime] = None
    """The date and time when the task was started."""

    task_url: Optional[str] = None
    """The presigned URL of the task."""
