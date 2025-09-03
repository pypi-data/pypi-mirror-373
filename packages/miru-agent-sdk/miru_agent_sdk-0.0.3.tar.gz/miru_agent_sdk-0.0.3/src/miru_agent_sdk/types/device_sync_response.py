# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DeviceSyncResponse"]


class DeviceSyncResponse(BaseModel):
    code: Literal["success", "network_connection_error", "in_cooldown"]
    """The result of attempting to sync the device."""

    cooldown_ends_at: datetime
    """Timestamp of when the cooldown will end"""

    in_cooldown: bool
    """Whether the device is currently in cooldown"""

    last_attempted_sync_at: datetime
    """Timestamp of when the last _attempted_ sync occurred"""

    last_synced_at: datetime
    """Timestamp of when the device was last synced"""

    message: str
    """The message of the result."""
