"""BasicAuthUserRepository class for the basic auth user."""

from __future__ import annotations

import datetime
import logging

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
from zmp_authentication_provider.scheme.auth_model import BasicAuthUser
from zmp_authentication_provider.utils.encryption_utils import decrypt, encrypt

log = logging.getLogger(__name__)

DEFAULT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
"""Default time format and time zone %Y-%m-%dT%H:%M:%S%z"""
DEFAULT_TIME_ZONE = datetime.UTC
"""Default time zone is UTC(+00:00)"""


class BasicAuthUserRepository:
    """BasicAuthUserRepository class."""

    def __init__(self, *, collection: AsyncIOMotorCollection):
        """Initialize the repository with MongoDB database."""
        self._collection = collection

    @classmethod
    async def create(cls, *, collection: AsyncIOMotorCollection) -> BasicAuthUserRepository:
        """Create a new instance of the repository."""
        instance = cls(collection=collection)
        await instance.init_index()
        return instance
    
    async def init_index(self) -> None:
        """Create indexes for the collection."""
        indexes = await self._collection.list_indexes().to_list(length=None)

        unique_index_name = "unique_key_username"

        unique_index_exists = False
        for index in indexes:
            if index["name"] == unique_index_name and index.get("unique", True):
                unique_index_exists = True
                break

        if not unique_index_exists:
            self._collection.create_index(
                "username", name=unique_index_name, unique=True
            )

        return self

    async def insert(self, basic_auth_user: BasicAuthUser) -> str:
        """Insert a basic auth user."""
        if basic_auth_user.created_at is None:
            basic_auth_user.created_at = datetime.datetime.now(DEFAULT_TIME_ZONE)

        # encrypt the token data
        basic_auth_user.password = encrypt(basic_auth_user.password).hex()

        basic_auth_user_dict = basic_auth_user.model_dump(by_alias=True, exclude=["id"])
        basic_auth_user_dict.update({"created_at": basic_auth_user.created_at})

        try:
            result: InsertOneResult = await self._collection.insert_one(
                basic_auth_user_dict
            )
        except DuplicateKeyError as e:
            raise ValueError(f"BasicAuthUser already exists: {e}")

        return str(result.inserted_id)

    async def find(self) -> list[BasicAuthUser]:
        """Find all basic auth users."""
        cursor = self._collection.find().sort("created_at", pymongo.DESCENDING)
        basic_auth_users = []
        async for document in cursor:
            if document is not None:
                basic_auth_user = BasicAuthUser(**document)
                # decrypt the token data
                basic_auth_user.password = decrypt(
                    bytes.fromhex(basic_auth_user.password)
                )
                basic_auth_users.append(basic_auth_user)

        return basic_auth_users
        # return [BasicAuthUser(**document) for document in cursor if document is not None]

    async def update(self, basic_auth_user: BasicAuthUser) -> BasicAuthUser:
        """Update a basic auth user."""
        try:
            query = {"_id": ObjectId(basic_auth_user.id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        if basic_auth_user.updated_at is None:
            basic_auth_user.updated_at = datetime.datetime.now(DEFAULT_TIME_ZONE)

        # encrypt the token data
        basic_auth_user.password = encrypt(basic_auth_user.password).hex()

        basic_auth_user_dict = basic_auth_user.model_dump(
            by_alias=True, exclude=["id", "created_at"]
        )
        basic_auth_user_dict.update({"updated_at": basic_auth_user.updated_at})
        update = {"$set": basic_auth_user_dict}
        # update = {"$set": basic_auth_user.model_dump(by_alias=True, exclude=['id', 'created_at'])}

        log.debug(f"Update basic_auth_user: {basic_auth_user.id}")
        log.debug(f"Update data: {update}")

        document = await self._collection.find_one_and_update(
            query, update=update, return_document=pymongo.ReturnDocument.AFTER
        )

        if document is None:
            raise ObjectNotFoundException(object_id=basic_auth_user.id)

        updated = BasicAuthUser(**document)

        # decrypt the token data
        updated.password = decrypt(bytes.fromhex(updated.password))
        return updated

    async def find_by_id(self, basic_auth_user_id: str) -> BasicAuthUser:
        """Find a basic auth user by id."""
        if not basic_auth_user_id:
            raise InvalidObjectIDException("BasicAuthUser id is required")

        try:
            query = {"_id": ObjectId(basic_auth_user_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        document = await self._collection.find_one(query)

        if document is None:
            raise ObjectNotFoundException(object_id=basic_auth_user_id)

        basic_auth_user = BasicAuthUser(**document)

        # decrypt the token data
        basic_auth_user.password = decrypt(bytes.fromhex(basic_auth_user.password))
        return basic_auth_user

    async def find_by_username(self, basic_auth_username: str) -> BasicAuthUser:
        """Find a basic auth user by username."""
        if not basic_auth_username:
            raise InvalidObjectIDException("BasicAuthUser username is required")

        document = await self._collection.find_one({"username": basic_auth_username})

        if document is None:
            raise ObjectNotFoundException(object_id=basic_auth_username)

        basic_auth_user = BasicAuthUser(**document)

        # decrypt the token data
        basic_auth_user.password = decrypt(bytes.fromhex(basic_auth_user.password))
        return basic_auth_user

    async def delete_by_id(self, basic_auth_user_id: str) -> bool:
        """Delete a basic auth user by id."""
        if not basic_auth_user_id:
            raise InvalidObjectIDException("BasicAuthUser id is required")

        try:
            query = {"_id": ObjectId(basic_auth_user_id)}
        except InvalidId as e:
            raise InvalidObjectIDException(e)

        result = await self._collection.find_one_and_delete(query)

        if result is None:
            raise ObjectNotFoundException(
                f"BasicAuthUser not found: {basic_auth_user_id}"
            )

        return True
