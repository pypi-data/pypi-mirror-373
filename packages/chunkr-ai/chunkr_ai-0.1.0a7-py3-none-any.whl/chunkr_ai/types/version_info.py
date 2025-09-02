# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["VersionInfo", "ClientVersion", "ClientVersionManualSDK", "ClientVersionGeneratedSDK"]


class ClientVersionManualSDK(BaseModel):
    manual_sdk: str = FieldInfo(alias="ManualSdk")
    """Version of the current manually-maintained SDK"""


class ClientVersionGeneratedSDK(BaseModel):
    generated_sdk: str = FieldInfo(alias="GeneratedSdk")
    """Version of the auto-generated SDK"""


ClientVersion: TypeAlias = Union[Literal["Legacy"], ClientVersionManualSDK, ClientVersionGeneratedSDK]


class VersionInfo(BaseModel):
    client_version: ClientVersion
    """The version of the client."""

    server_version: str
    """The version of the server."""
