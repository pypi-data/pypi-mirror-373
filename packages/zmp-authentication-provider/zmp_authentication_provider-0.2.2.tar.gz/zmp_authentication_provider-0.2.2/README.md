# ZMP Authentication Provider

A Python library for authentication using Basic Auth and OIDC (OpenID Connect).

## Description

This library provides authentication functionality using both Basic Authentication and OpenID Connect protocols. It's designed to be flexible and easy to integrate into your Python applications.

## Installation

```bash
pip install zmp-authentication-provider
```

## Requirements

- Python >= 3.12, < 4.0

## Dependencies

- pydantic >= 2.10.6
- pydantic-settings >= 2.9.1, < 3.0.0
- fastapi >= 0.115.11, < 0.116.0
- python-dotenv >= 1.0.1, < 2.0.0
- pyjwt >= 2.10.1, < 3.0.0
- requests >= 2.32.3, < 3.0.0
- cryptography >= 42.0.0, < 45.0
- pymongo >= 4.12.0, < 5.0.0
- motor >= 3.7.0, < 4.0.0

## Usage

```python
# FastAPI main.py
from zmp_authentication_provider.routes.auth import router as auth_router
from zmp_authentication_provider.service.auth_service import AuthService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for the FastAPI app."""
    try:
        # 8. Initialize AIOps Service
        app.state.aiops_service = AIOpsService.initialize(database=database)
        logger.info("AIOps Service initialized")

        yield

    finally:
        ...

app = FastAPI(
    # root_path=f"{application_settings.root_path}",
    title=f"{application_settings.title}",
    description=f"{application_settings.description}",
    version=f"{application_settings.version}",
    docs_url=f"{application_settings.docs_url}",
    openapi_url=f"{application_settings.openapi_url}",
    redoc_url=f"{application_settings.redoc_url}",
    default_response_class=JSONResponse,
    debug=True,
    # servers=server,
    root_path_in_servers=True,
    lifespan=lifespan,
)


app.include_router(auth_router, tags=["auth"], prefix=application_settings.root_path)


# router.py
from zmp_authentication_provider.auth.oauth2_keycloak import (
    TokenData,
    get_current_user,
)


@router.put(
    "/jobs/{job_id}",
    summary="Update job details",
    description="Update the details of an existing job. Only the provided fields will be updated.",
    response_description="The updated job information.",
    response_class=JSONResponse,
    response_model=Job,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def update_job(
    job_update_request: JobUpdateRequest,
    job_id: str = Path(..., description="The ID of the job to update"),
    service: AIOpsService = Depends(_get_aiops_service),
    oauth_user: TokenData = Depends(get_current_user),
):
    """Update a job's information."""
    job = Job(
        id=job_id,
        updated_by=oauth_user.username,
        **job_update_request.model_dump(exclude_unset=True),
    )
    return await service.modify_job(job=job)

```

### Environment Configuration

Put the below value into the`.env` file in your project root:

```env
# Authentication default configuration
AUTH_HTTP_CLIENT_SSL_VERIFY="True"
AUTH_APPLICATION_ENDPOINT="${AIOPS_API_ENDPOINT}"

# Keycloak configuration
KEYCLOAK_SERVER_URL="https://keycloak.ags.cloudzcp.net/auth"
KEYCLOAK_REALM="ags"
KEYCLOAK_CLIENT_ID="zmp-client"
KEYCLOAK_CLIENT_SECRET="p4W697V2t9WXSh3kCnCfSCt4MHK4myYG"
KEYCLOAK_REDIRECT_URI="${AUTH_APPLICATION_ENDPOINT}/oauth2/callback"
KEYCLOAK_ALGORITHM="RS256"
```

## Development

### Development Dependencies

```bash
pip install pytest pytest-cov pytest-watcher pytest-asyncio certifi ruff
```

### Quality Tools

```bash
pip install pre-commit
```

## Project Structure

The main package is located in the `src/zmp_authentication_provider` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

## Author

- Kilsoo Kang (kilsoo75@gmail.com)

## Links

- [Homepage](https://github.com/cloudz-mp)
- [Repository](https://github.com/cloudz-mp/zmp-authentication-provider)
- [Documentation](https://github.com/cloudz-mp/zmp-authentication-provider)
- [Issue Tracker](https://github.com/cloudz-mp/zmp-authentication-provider/issues)
