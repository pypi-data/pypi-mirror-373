# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["BoundingBox"]


class BoundingBox(BaseModel):
    height: float
    """The height of the bounding box."""

    left: float
    """The left coordinate of the bounding box."""

    top: float
    """The top coordinate of the bounding box."""

    width: float
    """The width of the bounding box."""
