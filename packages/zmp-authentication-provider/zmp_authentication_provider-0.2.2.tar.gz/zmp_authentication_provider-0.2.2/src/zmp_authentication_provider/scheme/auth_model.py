"""Auth model module for the AIops Pilot."""

from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_serializer

PyObjectId = Annotated[str, BeforeValidator(str)]


class AuthBaseModel(BaseModel):
    """Auth Base Model.

    mongodb objectId _id issues

    refence:
    https://github.com/tiangolo/fastapi/issues/1515
    https://github.com/mongodb-developer/mongodb-with-fastapi
    """

    id: PyObjectId | None = Field(default=None, alias="_id")

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow",
    )

    @field_serializer("id")
    def _serialize_id(self, id: PyObjectId | None) -> str | None:
        if id is None:
            return None
        else:
            return str(id)

    @field_serializer("created_at", "updated_at")
    def _serialize_created_updated_at(self, dt: datetime | None) -> str | None:
        return dt.isoformat(timespec="milliseconds") if dt else None


class BasicAuthUser(AuthBaseModel):
    """Basic auth user model."""

    username: str
    password: str
    modifier: Optional[str] = None


class TokenData(BaseModel):
    """Token data model."""

    iss: str = Field(..., description="Issuer URL")
    sub: str = Field(..., description="Subject")
    username: str = Field(None, description="Username")
    email: str = Field(None, description="Email")
    given_name: str = Field(None, description="Given name")
    family_name: str = Field(None, description="Family name")
    # for backward compatibility of keycloak
    realm_roles: List[str] = Field(None, description="Realm roles")
    """
    {realm_access: [role1, role2, ...]}
    """
    realm_access: dict = Field(None, description="Realm access")
    """
    {realm_access: {roles: [role1, role2, ...]}}
    """
    resource_access: dict = Field(None, description="Resource access")


class OAuthUser(AuthBaseModel):
    """OAuth user model from IDP's user info using the id token."""

    iss: str = Field(..., description="Issuer URL")
    sub: str = Field(..., description="Subject. Unique user ID of the IDP")
    username: str = Field(..., description="Unique username (preferred_username)")
    email: str | None = Field(None, description="Email")
    given_name: str | None = Field(None, description="Given name")
    family_name: str | None = Field(None, description="Family name")
