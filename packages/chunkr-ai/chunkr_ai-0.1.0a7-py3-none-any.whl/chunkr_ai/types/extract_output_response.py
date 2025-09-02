# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ExtractOutputResponse"]


class ExtractOutputResponse(BaseModel):
    citations: object
    """Mirror of `results`; leaves are `Vec<Citation>` for the corresponding field"""

    metrics: object
    """
    Mirror of `results`; leaves contain a `Metrics` object for the corresponding
    field
    """

    results: object
    """JSON data that matches the provided schema"""
