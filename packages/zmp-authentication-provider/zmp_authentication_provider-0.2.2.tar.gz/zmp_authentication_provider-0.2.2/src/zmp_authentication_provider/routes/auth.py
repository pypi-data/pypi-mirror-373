"""Auth routes."""

import base64
import json
import logging
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from zmp_authentication_provider.auth.oauth2_keycloak import (
    KEYCLOAK_AUTH_ENDPOINT,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_END_SESSION_ENDPOINT,
    KEYCLOAK_REDIRECT_URI,
    KEYCLOAK_TOKEN_ENDPOINT,
    KEYCLOAK_USER_ENDPOINT,
    TokenData,
    get_current_user,
    verify_token,
)
from zmp_authentication_provider.auth.session_auth import (
    USER_SESSION_KEY,
    get_current_user_in_session,
)
from zmp_authentication_provider.exceptions import (
    AuthBackendException,
    AuthError,
)
from zmp_authentication_provider.routes import get_auth_service
from zmp_authentication_provider.scheme.auth_model import OAuthUser
from zmp_authentication_provider.service.auth_service import AuthService
from zmp_authentication_provider.setting import auth_default_settings
from zmp_authentication_provider.utils.session_memory import (
    InMemorySessionStore,
    SessionData,
)

logger = logging.getLogger(__name__)


in_memory_session_store = InMemorySessionStore(
    session_ttl=auth_default_settings.session_ttl,
    session_cleanup_interval=auth_default_settings.session_cleanup_interval,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/home", summary="Home page", response_class=HTMLResponse)
async def home(request: Request):  # , csrf_token: str = Depends(csrf_scheme)):
    """Get home page."""
    # check the session_id in the cookie
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)

    logger.debug(f"csrf_token: {csrf_token}")
    logger.debug(f"session_id: {session_id}")

    if csrf_token and session_id:
        user_info = request.session.get("user_info")
        if not user_info:
            request.session.clear()
            return HTMLResponse(
                content="Session data has been lost "
                "because the server has been restared."
                "Please login again",
            )
        else:
            return HTMLResponse(content=f"<p>User info</p><p>{user_info}</p>")
    else:
        return HTMLResponse(content="<p>No user info. Please login again.</p>")


@router.get(
    "/authenticate",
    summary="Process the authentication",
    response_class=RedirectResponse,
)
async def authenticate(request: Request):
    """Authenticate whether the user is logged in or not."""
    # check the session_id in the cookie
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)

    logger.debug(f"csrf_token: {csrf_token}")
    logger.debug(f"session_id: {session_id}")

    # for the redirect to the referer
    referer = request.headers.get("referer")
    # referer = referer or "/"
    if not referer:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="Referer is not found in the request header",
        )

    logger.debug(f"referer: {referer}")

    if csrf_token and session_id:
        access_token = request.session.get("access_token")
        if not access_token:
            request.session.clear()
            logger.error(
                "Session data has been lost "
                "because the server has been restared."
                "Please login again",
            )
            return RedirectResponse(
                url=f"{KEYCLOAK_AUTH_ENDPOINT}?response_type=code"
                f"&client_id={KEYCLOAK_CLIENT_ID}"
                f"&state={csrf_token}{auth_default_settings.state_separator}{referer}"
                f"&redirect_uri={KEYCLOAK_REDIRECT_URI}"
                f"&scope=openid profile email"
                # NOTE: referer is not used in the keycloak
                # f"&referer={referer}"
            )
        else:
            logger.debug(f"access_token: {access_token[:100]}...")

            return RedirectResponse(url=f"{referer}")
    else:
        return RedirectResponse(
            url=f"{KEYCLOAK_AUTH_ENDPOINT}?response_type=code"
            f"&client_id={KEYCLOAK_CLIENT_ID}"
            f"&state={csrf_token}{auth_default_settings.state_separator}{referer}"
            f"&redirect_uri={KEYCLOAK_REDIRECT_URI}"
            f"&scope=openid profile email"
            # NOTE: referer is not used in the keycloak
            # f"&referer={referer}"
        )


@router.get(
    "/logout",
    summary="Logout from the keyclaok",
    response_class=RedirectResponse,
)
async def logout(
    request: Request,
    # csrf_token: str = Depends(csrf_scheme),
    # session_id: str = Depends(session_id_scheme)
):
    """Logout."""
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)
    session_id = request.cookies.get(auth_default_settings.session_id_cookie_name)
    if not csrf_token or not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No csrf token in cookie and session id in cookie",
        )
    else:
        user_info = request.session.get("user_info")
        if not user_info:
            raise AuthBackendException(
                AuthError.OAUTH_IDP_ERROR,
                details="User info is not found in the request session",
            )
        user_id = user_info.get("sub")
        if not user_id:
            raise AuthBackendException(
                AuthError.OAUTH_IDP_ERROR,
                details="User ID is not found in the user info",
            )
        session_data = in_memory_session_store.get(user_id)
        if not session_data:
            raise AuthBackendException(
                AuthError.OAUTH_IDP_ERROR,
                details="Session data is not found in the in-memory session store",
            )

        # refresh_token = request.session.get("refresh_token")
        refresh_token = session_data.refresh_token
        if not refresh_token:
            raise AuthBackendException(
                AuthError.OAUTH_IDP_ERROR,
                details="Refresh token is not found in the session data",
            )
        else:
            # 1. logout from the keycloak
            data = {
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "refresh_token": refresh_token,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            idp_response = requests.post(
                KEYCLOAK_END_SESSION_ENDPOINT,
                data=data,
                headers=headers,
                verify=auth_default_settings.http_client_ssl_verify,
            )  # verify=False: because of the SKCC self-signed certificate

            if idp_response.status_code != 204:
                raise AuthBackendException(
                    AuthError.OAUTH_IDP_ERROR,
                    details=f"Failed to logout.({idp_response.reason})",
                )
        # 2. delete the session data from the in-memory session store
        in_memory_session_store.delete(user_id)
        # 3. clear the session
        request.session.clear()

        # NOTE: go to the authenticate endpoint with the referer (/) after logout
        redirect_response = RedirectResponse(
            url=f"{auth_default_settings.application_endpoint}/auth/authenticate",
            headers={"referer": "/"},
        )
        # clear the csrf token cookie
        # NOTE: the csrf token cookie should be kept for the next request
        # redirect_response.delete_cookie(
        #     key=auth_default_settings.csrf_token_cookie_name
        # )

        return redirect_response


@router.get("/oauth2/callback", summary="Keycloak OAuth2 callback for the redirect URI")
async def callback(
    request: Request,
    code: str,
    state: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Keycloak OAuth2 callback for the redirect URI."""
    csrf_token = request.cookies.get(auth_default_settings.csrf_token_cookie_name)

    state = state.split(auth_default_settings.state_separator)
    received_csrf_token = state[0]
    referer = state[1]

    logger.debug(f"cookie csrftoken: {csrf_token}")
    logger.debug(f"state: {state}")
    logger.debug(f"received csrftoken: {received_csrf_token}")
    logger.debug(f"referer: {referer}")

    if received_csrf_token != csrf_token:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"CSRF token mismatch.({received_csrf_token} != {csrf_token})",
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": KEYCLOAK_REDIRECT_URI,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    idp_response = requests.post(
        KEYCLOAK_TOKEN_ENDPOINT,
        data=data,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )

    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to obtain token.({idp_response.reason})",
        )

    tokens = idp_response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    id_token = tokens.get("id_token")

    # NOTE: This is not needed anymore because the access token is used for the authentication
    # -----------------------------------------------------------------------------------------
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    idp_response = requests.get(
        KEYCLOAK_USER_ENDPOINT,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )
    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to fetch user info.({idp_response.reason})",
        )

    user_info = idp_response.json()
    logger.debug(f"user_info: {user_info}")
    user_id = user_info.get("sub")
    if not user_id:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="User ID is not found in the user info",
        )

    # -----------------------------------------------------------------------------------------
    # NOTE: the user_info is only used for the authentication
    request.session[USER_SESSION_KEY] = user_info

    # check the session data size because the max size of the cookie is 4kb
    json_session = json.dumps(request.session)
    logger.debug(f"json_session: {json_session}")
    logger.debug(f"json_session bytes: {len(json_session.encode('utf-8'))}")

    base64_encoded_session = base64.b64encode(json_session.encode("utf-8"))
    logger.debug(f"base64_encoded_session: {base64_encoded_session}")

    total_bytes = len(base64_encoded_session)
    logger.debug(f"base64_encoded_session bytes: {total_bytes}")

    if total_bytes > (4 * 1024):
        logger.debug(f"Total bytes: {total_bytes}")
        logger.warning(f"The session data size({total_bytes}) is over than 4kb.")
        raise AuthBackendException(
            AuthError.TOKEN_DATA_TOO_LARGE,
            details=f"The session data size is {total_bytes} bytes. It is over than 4kb.",
        )

    # store the session data in the in-memory session store
    session_data = SessionData(
        user_info=user_info,
        access_token=access_token,
        refresh_token=refresh_token,
        id_token=id_token,
    )
    in_memory_session_store.set(user_id, session_data)

    # -----------------------------------------------------------------------------------------
    # create the oauth user if the enable_oauth_user_creation is True
    if auth_default_settings.enable_oauth_user_creation:
        # NOTE: the userinfo does not have the iss, so we need to verify the id_token for OAuthUser creation
        token_data = verify_token(id_token)
        oauth_user = OAuthUser(
            iss=token_data.iss,
            sub=token_data.sub,
            username=token_data.username,
            email=token_data.email,
            given_name=token_data.given_name,
            family_name=token_data.family_name,
        )

        logger.debug(f"oauth_user: {oauth_user}")

        await auth_service.upsert_oauth_user(oauth_user)

    # If the same-site of cookie is 'lax', the cookie will be sent only if the request is same-site request
    # If the same-site of cookie is 'strict', the cookie will not be sent
    return RedirectResponse(
        # url=f"{auth_default_settings.application_endpoint}/auth/home"
        url=f"{referer}"
    )


@router.get(
    "/access_token", summary="Get the access token from the in-memory session store"
)
async def get_access_token(
    user_info: dict[str, Any] = Depends(get_current_user_in_session),
):
    """Get the access token from the in-memory session store."""
    user_id = user_info.get("sub")
    if not user_id:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="User ID is not found in the user info",
        )

    session_data = in_memory_session_store.get(user_id)
    if not session_data:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="Session data is not found in the in-memory session store",
        )
    return {"access_token": session_data.access_token}


@router.patch(
    "/refresh_token", summary="Refresh the access token using the refresh token"
)
async def refresh_access_token(
    user_info: dict[str, Any] = Depends(get_current_user_in_session),
):
    """Refresh the access token using the refresh token."""
    user_id = user_info.get("sub")
    if not user_id:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="User ID is not found in the user info",
        )

    session_data = in_memory_session_store.get(user_id)
    if not session_data:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="Session data is not found in the in-memory session store",
        )

    refresh_token = session_data.refresh_token
    if not refresh_token:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="Refresh token is not found in the session data",
        )

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    idp_response = requests.post(
        KEYCLOAK_TOKEN_ENDPOINT,
        data=data,
        headers=headers,
        verify=auth_default_settings.http_client_ssl_verify,
    )

    if idp_response.status_code != 200:
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details=f"Failed to refresh the access token.({idp_response.reason})",
        )

    refreshed_tokens = idp_response.json()
    # TODO: check the tokens whether the access token, refresh token, and id token are included in the tokens
    logger.debug(f"tokens: {refreshed_tokens}")

    if not refreshed_tokens.get("access_token"):
        raise AuthBackendException(
            AuthError.OAUTH_IDP_ERROR,
            details="Access token is not found in the response",
        )
    else:
        # update the session data in the in-memory session store with the new tokens
        session_data = SessionData(
            user_info=user_info,
            access_token=refreshed_tokens.get("access_token"),
            refresh_token=refreshed_tokens.get("refresh_token"),
            id_token=refreshed_tokens.get("id_token"),
        )
        in_memory_session_store.set(user_id, session_data)

        return {"access_token": session_data.access_token}


@router.get("/profile", summary="Get the current user profile from Token")
async def profile(oauth_user: TokenData = Depends(get_current_user)):
    """Get the current user profile from Token."""
    session_data = in_memory_session_store.get(oauth_user.sub)
    if not session_data:
        raise AuthBackendException(
            AuthError.SESSION_EXPIRED,
            details="Session data is not found in the in-memory session store",
        )
    in_memory_session_store.reset_ttl(oauth_user.sub)

    return oauth_user
