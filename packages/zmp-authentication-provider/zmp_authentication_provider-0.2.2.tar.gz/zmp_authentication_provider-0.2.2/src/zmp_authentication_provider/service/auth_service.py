"""AuthService class to handle auth service."""

from __future__ import annotations

import logging
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from zmp_authentication_provider.db.basic_auth_user_repository import (
    BasicAuthUserRepository,
)
from zmp_authentication_provider.db.oauth_user_repository import (
    OAuthUserRepository,
)
from zmp_authentication_provider.exceptions import (
    AuthBackendException,
    AuthError,
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from zmp_authentication_provider.scheme.auth_model import BasicAuthUser, OAuthUser
from zmp_authentication_provider.setting import auth_default_settings

log = logging.getLogger(__name__)


class AuthService:
    """AuthService class to handle auth service."""

    def __init__(self, *, database: AsyncIOMotorDatabase):
        """Initialize the repository with MongoDB database."""
        self._database = database
        self._basic_auth_user_repository: BasicAuthUserRepository = None
        self._oauth_user_repository: OAuthUserRepository = None

    @classmethod
    async def initialize(cls, *, database: AsyncIOMotorDatabase) -> AuthService:
        """Create a new instance of the service."""
        instance = cls(database=database)
        instance._basic_auth_user_repository = await BasicAuthUserRepository.create(
            collection=instance._database[
                auth_default_settings.basic_auth_user_collection
            ]
        )
        instance._oauth_user_repository = await OAuthUserRepository.create(
            collection=instance._database[auth_default_settings.oauth_user_collection]
        )
        log.info(f"{__name__} AuthService Initialized")

        return instance

    async def create_basic_auth_user(self, user: BasicAuthUser) -> str:
        """Create a basic auth user."""
        try:
            return await self._basic_auth_user_repository.insert(user)
        except ValueError as e:
            raise AuthBackendException(AuthError.BAD_REQUEST, details=str(e))

    async def modify_basic_auth_user(self, user: BasicAuthUser) -> BasicAuthUser:
        """Update a basic auth user."""
        try:
            return await self._basic_auth_user_repository.update(user)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=user.id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def remove_basic_auth_user(self, id: str) -> bool:
        """Delete a basic auth user by id."""
        if not id:
            raise AuthBackendException(AuthError.BAD_REQUEST, details="ID is required")

        try:
            return await self._basic_auth_user_repository.delete_by_id(id)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_basic_auth_user_by_username(self, username: str) -> BasicAuthUser:
        """Get a basic auth user by username."""
        if not username:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Username is required"
            )

        try:
            return await self._basic_auth_user_repository.find_by_username(username)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=username,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_basic_auth_users(self) -> List[BasicAuthUser]:
        """Get basic auth users."""
        return await self._basic_auth_user_repository.find()

    async def create_oauth_user(self, user: OAuthUser) -> str:
        """Create an OAuth user."""
        try:
            return await self._oauth_user_repository.insert(user)
        except ValueError as e:
            raise AuthBackendException(AuthError.BAD_REQUEST, details=str(e))

    async def modify_oauth_user(self, user: OAuthUser) -> OAuthUser:
        """Update an OAuth user."""
        try:
            return await self._oauth_user_repository.update(user)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=user.id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def remove_oauth_user(self, id: str) -> bool:
        """Delete an OAuth user by id."""
        if not id:
            raise AuthBackendException(AuthError.BAD_REQUEST, details="ID is required")

        try:
            return await self._oauth_user_repository.delete_by_id(id)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_oauth_user_by_sub(self, sub: str) -> OAuthUser:
        """Get an OAuth user by sub field."""
        if not sub:
            raise AuthBackendException(AuthError.BAD_REQUEST, details="Sub is required")

        try:
            return await self._oauth_user_repository.find_by_sub(sub)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=sub,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_oauth_user_by_username(self, username: str) -> OAuthUser:
        """Get an OAuth user by username field."""
        if not username:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Username is required"
            )

        try:
            return await self._oauth_user_repository.find_by_username(username)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=username,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_oauth_user_by_email(self, email: str) -> OAuthUser:
        """Get an OAuth user by email."""
        if not email:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Email is required"
            )

        try:
            return await self._oauth_user_repository.find_by_email(email)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=email,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_oauth_user_by_sub_and_issuer(self, sub: str, iss: str) -> OAuthUser:
        """Get an OAuth user by sub and issuer."""
        if not sub:
            raise AuthBackendException(AuthError.BAD_REQUEST, details="Sub is required")
        if not iss:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Issuer is required"
            )

        try:
            return await self._oauth_user_repository.find_by_sub_and_issuer(sub, iss)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.oauth_user_collection,
                object_id=f"{sub}@{iss}",
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_oauth_users(self) -> List[OAuthUser]:
        """Get OAuth users."""
        return await self._oauth_user_repository.find()

    async def upsert_oauth_user(self, user: OAuthUser) -> OAuthUser:
        """Create or update an OAuth user based on sub and issuer."""
        if not user.sub:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Sub is required for upsert operation"
            )
        if not user.iss:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Issuer is required for upsert operation"
            )

        try:
            # Try to find existing user by sub and issuer
            existing_user = await self._oauth_user_repository.find_by_sub_and_issuer(
                user.sub, user.iss
            )
            # Update existing user
            user.id = existing_user.id
            user.created_at = existing_user.created_at  # Preserve creation time
            return await self._oauth_user_repository.update(user)
        except ObjectNotFoundException:
            # Create new user if not found
            await self._oauth_user_repository.insert(user)
            # Return the created user by finding it again to get the generated ID
            return await self._oauth_user_repository.find_by_sub_and_issuer(
                user.sub, user.iss
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))
        except ValueError as e:
            raise AuthBackendException(AuthError.BAD_REQUEST, details=str(e))
