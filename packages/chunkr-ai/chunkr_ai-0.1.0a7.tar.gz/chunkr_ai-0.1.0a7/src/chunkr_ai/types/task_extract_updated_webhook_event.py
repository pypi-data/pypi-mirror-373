# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TaskExtractUpdatedWebhookEvent"]


class TaskExtractUpdatedWebhookEvent(BaseModel):
    event_type: Literal["task.parse.updated", "task.extract.updated"]
    """Event type identifier"""

    status: Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]
    """Current status of the task"""

    task_id: str
    """Unique task identifier"""

    message: Optional[str] = None
    """Optional human-readable status message"""
