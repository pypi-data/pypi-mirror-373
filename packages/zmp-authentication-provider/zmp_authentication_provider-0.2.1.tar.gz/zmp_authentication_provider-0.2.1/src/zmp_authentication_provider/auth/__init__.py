"""Auth module for the AIops Pilot."""

from .basic_auth import get_current_user_for_basicauth
from .oauth2_keycloak import get_current_user

__all__ = ["get_current_user", "get_current_user_for_basicauth"]
