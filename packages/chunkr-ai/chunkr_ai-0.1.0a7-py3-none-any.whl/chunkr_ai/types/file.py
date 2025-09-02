# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel

__all__ = ["File"]


class File(BaseModel):
    content_type: str
    """MIME type detected or provided for the file."""

    created_at: datetime
    """Timestamp when the file was created."""

    file_id: str
    """Unique identifier for the file."""

    file_name: str
    """The original filename supplied by the client."""

    file_size: int
    """Size of the stored file in bytes."""

    metadata: object
    """Arbitrary JSON metadata associated with the file."""

    url: str
    """Permanent Chunkr URL. Use directly with other chunkr API requests."""
