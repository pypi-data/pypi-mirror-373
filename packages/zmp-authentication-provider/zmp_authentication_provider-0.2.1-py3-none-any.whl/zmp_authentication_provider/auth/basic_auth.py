"""Basic auth module for the AIops Pilot."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from zmp_authentication_provider.scheme.auth_model import BasicAuthUser
from zmp_authentication_provider.service.auth_service import AuthService
from zmp_authentication_provider.setting import auth_default_settings

basic_security = HTTPBasic()


def verify_basic_auth_user(service: AuthService, credentials: HTTPBasicCredentials):
    """Verify the basic auth user."""
    user: BasicAuthUser = service.get_basic_auth_user_by_username(credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{credentials.username} not found",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )

    return BasicAuthUser(username=credentials.username, password=credentials.password)


def get_current_user_for_basicauth(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(basic_security),
) -> BasicAuthUser:
    """Get the current user for basic auth."""
    service = getattr(request.app.state, auth_default_settings.service_name, None)
    if not service:
        raise HTTPException(
            status_code=500,
            detail=f"Service '{auth_default_settings.service_name}' not available in the request state. "
            "You should set the service in the request state.",
        )

    return verify_basic_auth_user(service=service, credentials=credentials)
