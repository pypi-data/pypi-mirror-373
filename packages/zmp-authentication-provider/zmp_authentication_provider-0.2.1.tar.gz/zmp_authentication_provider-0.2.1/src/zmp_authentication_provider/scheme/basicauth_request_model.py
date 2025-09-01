"""This module contains the request models for the basic auth user."""

from typing import Optional

from pydantic import BaseModel, Field


class BasicAuthUserCreateRequest(BaseModel):
    """Request model for creating a basic auth user."""
    username: Optional[str] = Field(max_length=100, min_length=3)
    password: Optional[str] = Field(max_length=100, min_length=8)


class BasicAuthUserUpdateRequest(BasicAuthUserCreateRequest):
    """Request model for updating a basic auth user."""

