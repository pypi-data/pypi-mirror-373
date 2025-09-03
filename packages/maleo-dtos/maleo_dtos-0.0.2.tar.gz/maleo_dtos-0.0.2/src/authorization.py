import httpx
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from typing import Generator, Generic, Optional, TypeVar


class Authorization(BaseModel):
    scheme: str = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")

    @classmethod
    def from_request(cls, token: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        return cls(scheme=token.scheme, credentials=token.credentials)


AuthorizationT = TypeVar("AuthorizationT", bound=Optional[Authorization])


class AuthorizationMixin(BaseModel, Generic[AuthorizationT]):
    authorization: AuthorizationT = Field(
        ...,
        description="Authorization",
    )


class BearerAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self._auth_header = self._build_auth_header(token)

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = self._auth_header
        yield request

    def _build_auth_header(self, token: str) -> str:
        return f"Bearer {token}"
