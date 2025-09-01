"""OAuth2 Keycloak module for the AIops Pilot."""

import logging
from typing import Any

from fastapi import HTTPException, Request, status

log = logging.getLogger(__name__)

USER_SESSION_KEY = "user_info"


async def get_current_user_in_session(request: Request) -> dict[str, Any]:
    """Get the user info from the request."""
    user_info: dict[str, Any] = request.session.get(USER_SESSION_KEY)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User info is not found in the request session",
        )

    return user_info
