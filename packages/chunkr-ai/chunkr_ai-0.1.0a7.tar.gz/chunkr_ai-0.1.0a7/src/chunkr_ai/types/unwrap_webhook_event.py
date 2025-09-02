# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import TypeAlias

from .task_parse_updated_webhook_event import TaskParseUpdatedWebhookEvent
from .task_extract_updated_webhook_event import TaskExtractUpdatedWebhookEvent

__all__ = ["UnwrapWebhookEvent"]

UnwrapWebhookEvent: TypeAlias = Union[TaskExtractUpdatedWebhookEvent, TaskParseUpdatedWebhookEvent]
