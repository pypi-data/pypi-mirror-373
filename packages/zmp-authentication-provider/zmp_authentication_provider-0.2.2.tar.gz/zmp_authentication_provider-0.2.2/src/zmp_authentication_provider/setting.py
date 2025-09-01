"""Base settings for MCP and Gateway."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakSettings(BaseSettings):
    """Settings for Keycloak."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="KEYCLOAK_", env_file=".env", extra="ignore"
    )

    server_url: str
    realm: str
    client_id: str
    client_secret: str
    redirect_uri: str
    algorithm: str = "RS256"


keycloak_settings = KeycloakSettings()


class RedisSettings(BaseSettings):
    """Settings for Redis."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="REDIS_", env_file=".env", extra="ignore"
    )

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    decode_responses: bool = True
    session_prefix: str = "session:"
    session_ttl: int = 3600  # 1 hour default


redis_settings = RedisSettings()


class AuthDefaultSettings(BaseSettings):
    """Settings for Basic Auth."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="AUTH_", env_file=".env", extra="ignore"
    )

    # The name of the auth service
    service_name: str = "auth_service"

    # The api endpoint of the application which is used to redirect to the login page
    application_endpoint: str

    # The secret key for the encryption
    basic_auth_encryption_key: str = (
        "425df05bf30c8434e8a619563b602a7aa0421011f71727289eee66d310897118"
    )

    # The collection name for the basic auth user
    basic_auth_user_collection: str = "basic_auth_user"

    # The collection name for the OAuth user
    oauth_user_collection: str = "oauth_user"

    # The http client ssl verify
    http_client_ssl_verify: bool = True

    # The http client timeout
    http_client_timeout: int = 30

    # The csrf token cookie name
    csrf_token_cookie_name: str = "csrftoken"

    # The csrf token header name
    csrf_token_header_name: str = "x-csrftoken"

    # The session id cookie name
    session_id_cookie_name: str = "session_id"

    # state separator
    state_separator: str = "::"

    # Session middleware max_age (cookie expiration time)
    session_middleware_max_age: int = 1800  # 30 minutes

    # Session middleware same_site policy
    session_middleware_same_site: str = "lax"

    # Session middleware https_only
    session_middleware_https_only: bool = False

    # Session memory ttl
    session_ttl: int = 3600  # 1 hour default
    session_cleanup_interval: int = 300  # 5 minutes default

    # Flag to enable the OAuth user creation
    enable_oauth_user_creation: bool = False


auth_default_settings = AuthDefaultSettings()
