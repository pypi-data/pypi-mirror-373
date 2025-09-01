"""This module contains the routes for the basic auth user."""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse

from zmp_authentication_provider.auth.oauth2_keycloak import TokenData, get_current_user
from zmp_authentication_provider.routes import get_auth_service
from zmp_authentication_provider.scheme.auth_model import BasicAuthUser
from zmp_authentication_provider.scheme.basicauth_request_model import (
    BasicAuthUserCreateRequest,
    BasicAuthUserUpdateRequest,
)
from zmp_authentication_provider.service.auth_service import AuthService

log = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/basic_auth_users",
    summary="Get basic auth users",
    response_class=JSONResponse,
    response_model=List[BasicAuthUser],
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_basic_auth_users(
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> List[BasicAuthUser]:
    """Get all basic auth users."""
    return await auth_service.get_basic_auth_users()


@router.post(
    "/basic_auth_users",
    summary="Create a basic auth user",
    response_class=JSONResponse,
    response_model=Dict[str, str],
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def create_basic_auth_user(
    basic_auth_user_create_request: BasicAuthUserCreateRequest,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    """Create a basic auth user."""
    basic_auth_user = BasicAuthUser(**basic_auth_user_create_request.model_dump())
    basic_auth_user.modifier = oauth_user.username
    return {"inserted_id": await auth_service.create_basic_auth_user(basic_auth_user)}


@router.get(
    "/basic_auth_users/{username}",
    summary="Get a basic auth user by username",
    response_class=JSONResponse,
    response_model=BasicAuthUser,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_basic_auth_user_by_username(
    username: str,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> BasicAuthUser:
    """Get a basic auth user by username."""
    return await auth_service.get_basic_auth_user_by_username(username)


@router.delete(
    "/basic_auth_users/{id}",
    summary="Remove a basic auth user",
    response_class=JSONResponse,
    response_model=Dict[str, str],
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def remove_basic_auth_user(
    id: str,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    """Remove a basic auth user."""
    result = await auth_service.remove_basic_auth_user(id)
    return {"result": "success" if result else "failed"}


@router.put(
    "/basic_auth_users/{id}",
    summary="Modify a basic_auth_user",
    response_class=JSONResponse,
    response_model=BasicAuthUser,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def modify_basic_auth_user(
    basic_auth_user_update_request: BasicAuthUserUpdateRequest,
    id: str = Path(..., description="The id of the basic auth user"),
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> BasicAuthUser:
    """Modify a basic auth user."""
    basic_auth_user = BasicAuthUser(**basic_auth_user_update_request.model_dump())
    basic_auth_user.id = id
    basic_auth_user.modifier = oauth_user.username
    return await auth_service.modify_basic_auth_user(basic_auth_user)
