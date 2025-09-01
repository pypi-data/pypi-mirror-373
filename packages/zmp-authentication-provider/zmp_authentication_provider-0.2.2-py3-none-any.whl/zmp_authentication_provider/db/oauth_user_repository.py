"""OAuthUserRepository class for the OAuth user."""

from __future__ import annotations

import datetime
import logging
from typing import List

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult

from zmp_authentication_provider.exceptions import (
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from zmp_authentication_provider.scheme.auth_model import OAuthUser

log = logging.getLogger(__name__)

DEFAULT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""Default time format and time zone %Y-%m-%dT%H:%M:%S%z"""
DEFAULT_TIME_ZONE = datetime.UTC
"""Default time zone is UTC(+00:00)"""


class OAuthUserRepository:
    """OAuthUserRepository class."""

    def __init__(self, *, collection: AsyncIOMotorCollection):
        """Initialize the repository with MongoDB database."""
        self._collection = collection

    @classmethod
    async def create(cls, *, collection: AsyncIOMotorCollection) -> OAuthUserRepository:
        """Create a new instance of the repository."""
        instance = cls(collection=collection)
        await instance.init_index()
        return instance

    async def init_index(self) -> None:
        """Create indexes for the collection."""
        indexes = await self._collection.list_indexes().to_list(length=None)

        unique_index_name = "unique_key_sub_iss"
        email_index_name = "index_email"
        username_index_name = "index_username"

        unique_index_exists = False
        email_index_exists = False
        username_index_exists = False

        for index in indexes:
            if index["name"] == unique_index_name and index.get("unique", True):
                unique_index_exists = True
            if index["name"] == email_index_name:
                email_index_exists = True
            if index["name"] == username_index_name:
                username_index_exists = True

        if not unique_index_exists:
            await self._collection.create_index(
                [("sub", 1), ("iss", 1)], name=unique_index_name, unique=True
            )

        if not email_index_exists:
            await self._collection.create_index("email", name=email_index_name)

        if not username_index_exists:
            await self._collection.create_index("username", name=username_index_name)

        return self

    async def insert(self, oauth_user: OAuthUser) -> str:
        """Insert an OAuth user."""
        if oauth_user.created_at is None:
            oauth_user.created_at = datetime.datetime.now(DEFAULT_TIME_ZONE)

        oauth_user_dict = oauth_user.model_dump(by_alias=True, exclude=["id"])
        oauth_user_dict.update({"created_at": oauth_user.created_at})

        try:
            result: InsertOneResult = await self._collection.insert_one(oauth_user_dict)
        except DuplicateKeyError as e:
            raise ValueError(f"OAuthUser already exists: {e}")

        return str(result.inserted_id)

    async def find(self) -> List[OAuthUser]:
        """Find all OAuth users."""
        cursor = self._collection.find().sort("created_at", pymongo.DESCENDING)
        oauth_users = []
        async for document in cursor:
            if document is not None:
                oauth_user = OAuthUser(**document)
                oauth_users.append(oauth_user)

        return oauth_users

    async def update(self, oauth_user: OAuthUser) -> OAuthUser:
        """Update an OAuth user."""
        try:
            query = {"_id": ObjectId(oauth_user.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if oauth_user.updated_at is None:
            oauth_user.updated_at = datetime.datetime.now(DEFAULT_TIME_ZONE)

        oauth_user_dict = oauth_user.model_dump(
            by_alias=True, exclude=["id", "created_at"]
        )
        oauth_user_dict.update({"updated_at": oauth_user.updated_at})
        update = {"$set": oauth_user_dict}

        log.debug(f"Update oauth_user: {oauth_user.id}")
        log.debug(f"Update data: {update}")

        document = await self._collection.find_one_and_update(
            query, update=update, return_document=pymongo.ReturnDocument.AFTER
        )

        if document is None:
            raise ObjectNotFoundException(object_id=oauth_user.id)

        updated = OAuthUser(**document)
        return updated

    async def find_by_id(self, id: str) -> OAuthUser:
        """Find an OAuth user by id."""
        if not id:
            raise InvalidObjectIDException("OAuthUser id is required")

        try:
            query = {"_id": ObjectId(id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(query)

        if document is None:
            raise ObjectNotFoundException(object_id=id)

        oauth_user = OAuthUser(**document)
        return oauth_user

    async def find_by_sub(self, sub: str) -> OAuthUser:
        """Find an OAuth user by sub field."""
        if not sub:
            raise InvalidObjectIDException("OAuthUser sub is required")

        document = await self._collection.find_one({"sub": sub})

        if document is None:
            raise ObjectNotFoundException(object_id=sub)

        oauth_user = OAuthUser(**document)
        return oauth_user

    async def find_by_username(self, username: str) -> OAuthUser:
        """Find an OAuth user by username field."""
        if not username:
            raise InvalidObjectIDException("OAuthUser username is required")

        document = await self._collection.find_one({"username": username})

        if document is None:
            raise ObjectNotFoundException(object_id=username)

        oauth_user = OAuthUser(**document)
        return oauth_user

    async def find_by_email(self, email: str) -> OAuthUser:
        """Find an OAuth user by email."""
        if not email:
            raise InvalidObjectIDException("OAuthUser email is required")

        document = await self._collection.find_one({"email": email})

        if document is None:
            raise ObjectNotFoundException(object_id=email)

        oauth_user = OAuthUser(**document)
        return oauth_user

    async def find_by_sub_and_issuer(self, sub: str, iss: str) -> OAuthUser:
        """Find an OAuth user by sub and issuer."""
        if not sub:
            raise InvalidObjectIDException("OAuthUser sub is required")
        if not iss:
            raise InvalidObjectIDException("OAuthUser issuer is required")

        document = await self._collection.find_one({"sub": sub, "iss": iss})

        if document is None:
            raise ObjectNotFoundException(object_id=f"{sub}@{iss}")

        oauth_user = OAuthUser(**document)
        return oauth_user

    async def delete_by_id(self, oauth_user_id: str) -> bool:
        """Delete an OAuth user by id."""
        if not oauth_user_id:
            raise InvalidObjectIDException("OAuthUser id is required")

        try:
            query = {"_id": ObjectId(oauth_user_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        result = await self._collection.find_one_and_delete(query)

        if result is None:
            raise ObjectNotFoundException(f"OAuthUser not found: {oauth_user_id}")

        return True

    async def delete_by_sub(self, sub: str) -> bool:
        """Delete an OAuth user by sub."""
        if not sub:
            raise InvalidObjectIDException("OAuthUser sub is required")

        result = await self._collection.find_one_and_delete({"sub": sub})

        if result is None:
            raise ObjectNotFoundException(f"OAuthUser not found: {sub}")

        return True
