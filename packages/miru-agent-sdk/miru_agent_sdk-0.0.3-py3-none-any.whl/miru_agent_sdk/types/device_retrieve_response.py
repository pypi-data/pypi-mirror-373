# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DeviceRetrieveResponse"]


class DeviceRetrieveResponse(BaseModel):
    id: str
    """ID of the device"""

    last_connected_at: datetime
    """Timestamp of the last successful connection event with the backend."""

    last_disconnected_at: datetime
    """Timestamp of the last successful disconnection event with the backend."""

    last_synced_at: datetime
    """Timestamp of when the device was last synced"""

    name: str
    """Name of the device"""

    object: Literal["device"]

    status: Literal["online", "offline"]
    """The status of the device

    - Online: The miru agent is connected
    - Offline: The miru agent is disconnected (e.g. network issues, device is
      powered off, etc.)
    """
