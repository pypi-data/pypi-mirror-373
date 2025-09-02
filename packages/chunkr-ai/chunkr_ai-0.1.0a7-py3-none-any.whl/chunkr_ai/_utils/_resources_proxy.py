from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `chunkr_ai.resources` module.

    This is used so that we can lazily import `chunkr_ai.resources` only when
    needed *and* so that users can just import `chunkr_ai` and reference `chunkr_ai.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("chunkr_ai.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
