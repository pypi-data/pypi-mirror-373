"""Routes module for the authentication provider."""

from fastapi import Request
from fastapi.exceptions import HTTPException

from zmp_authentication_provider.service.auth_service import AuthService
from zmp_authentication_provider.setting import auth_default_settings


async def get_auth_service(request: Request) -> AuthService:
    """Get the auth service."""
    service = getattr(request.app.state, auth_default_settings.service_name, None)
    if not service:
        raise HTTPException(
            status_code=500,
            detail=f"Service '{auth_default_settings.service_name}' not available in the request state. "
            "You should set the service in the request state.",
        )

    return service


__all__ = ["get_auth_service"]
