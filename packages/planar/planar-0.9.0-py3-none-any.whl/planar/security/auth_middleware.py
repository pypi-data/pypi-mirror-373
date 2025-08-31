import jwt
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from planar.logging import get_logger
from planar.security.auth_context import (
    Principal,
    clear_principal,
    set_principal,
)

logger = get_logger(__name__)

BASE_JWKS_URL = "https://auth-api.coplane.com/sso/jwks"
EXPECTED_ISSUER = "https://auth-api.coplane.com"
SERVICE_TOKEN_HEADER_PREFIX = "Bearer plt_"


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        client_id: str,
        org_id: str,
        additional_exclusion_paths: list[str] | None = None,
        service_token: str | None = None,
    ):
        super().__init__(app)
        self.org_id = org_id
        self.additional_exclusion_paths = additional_exclusion_paths or []
        self.client = jwt.PyJWKClient(f"{BASE_JWKS_URL}/{client_id}", cache_keys=True)
        self.service_token = service_token

    def get_signing_key_from_jwt(self, token: str):
        return self.client.get_signing_key_from_jwt(token)

    def validate_jwt_token(self, token: str):
        signing_key = self.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=EXPECTED_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            },
        )

        org_id_from_token = payload.get("org_id")

        if (
            org_id_from_token is None
            or org_id_from_token == ""
            or org_id_from_token != self.org_id
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid organization",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    async def dispatch(self, request: Request, call_next):
        if request.url.path in (
            [
                "/planar/v1/health",
            ]
            + self.additional_exclusion_paths
        ):
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith(SERVICE_TOKEN_HEADER_PREFIX):
            return await self.dispatch_service_token(request, call_next)
        else:
            return await self.dispatch_jwt(request, call_next)

    async def dispatch_service_token(self, request: Request, call_next):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith(
            SERVICE_TOKEN_HEADER_PREFIX
        ):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication scheme"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_from_header = authorization.replace("Bearer ", "")
        if token_from_header != self.service_token:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid authentication credentials for service token"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        principal_token = None
        payload = {
            "sub": "service_token",
        }
        # Store payload in request state for backward compatibility
        request.state.user = payload
        # Create and set the principal in context
        principal = Principal.from_service_token(token_from_header)
        principal_token = set_principal(principal)

        try:
            response = await call_next(request)
        finally:
            # Clean up the principal context
            if principal_token is not None:
                clear_principal(principal_token)

        return response

    async def dispatch_jwt(self, request: Request, call_next):
        principal_token = None
        try:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication scheme"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = authorization.replace("Bearer ", "")
            payload = self.validate_jwt_token(token)

            # Store payload in request state for backward compatibility
            request.state.user = payload

            # Create and set the principal in context
            principal = Principal.from_jwt_payload(payload)
            principal_token = set_principal(principal)

        except ValueError:
            # Handle invalid JWT payload structure
            logger.exception("invalid jwt payload structure")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid JWT payload structure"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException as e:
            raise e
        except Exception:
            logger.exception("error validating jwt token")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            response = await call_next(request)
        finally:
            # Clean up the principal context
            if principal_token is not None:
                clear_principal(principal_token)

        return response
