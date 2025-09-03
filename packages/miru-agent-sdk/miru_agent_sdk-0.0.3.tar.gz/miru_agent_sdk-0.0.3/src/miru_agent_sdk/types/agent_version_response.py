# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["AgentVersionResponse"]


class AgentVersionResponse(BaseModel):
    commit: str
    """The commit hash of the agent"""

    version: str
    """The version of the agent"""
