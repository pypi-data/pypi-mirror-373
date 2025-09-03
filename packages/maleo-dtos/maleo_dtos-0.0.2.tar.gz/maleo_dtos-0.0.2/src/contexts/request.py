from datetime import datetime
from fastapi import Request
from pydantic import BaseModel, Field
from typing import Generic, List, Optional, Tuple, TypeVar
from uuid import UUID
from maleo.mixins.request import RequestIdentifier
from maleo.mixins.timestamp import RequestTimestamp
from maleo.types.base.boolean import OptionalBoolean
from maleo.types.base.dict import OptionalStringToStringDict
from maleo.types.base.string import OptionalString
from maleo.utils.extractor import extract_client_ip
from ..user_agent import UserAgent


class RequestContext(
    RequestTimestamp,
    RequestIdentifier,
):
    method: str = Field(..., description="Request's method")
    url: str = Field(..., description="Request's URL")
    ip_address: str = Field("unknown", description="Client's IP address")
    is_internal: OptionalBoolean = Field(None, description="True if IP is internal")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Request's headers"
    )
    path_params: OptionalStringToStringDict = Field(
        None, description="Request's path parameters"
    )
    query_params: OptionalString = Field(None, description="Request's query parameters")
    user_agent: UserAgent = Field(..., description="User agent")
    referer: OptionalString = Field(None, description="Referrer URL")
    origin: OptionalString = Field(None, description="Origin of the request")
    host: OptionalString = Field(None, description="Host header from request")
    forwarded_proto: OptionalString = Field(
        None, description="Forwarded protocol (http/https)"
    )
    language: OptionalString = Field(None, description="Accepted languages from client")

    @classmethod
    def from_request(cls, request: Request):
        id = request.state.id
        if not isinstance(id, UUID):
            raise ValueError(f"Invalid 'id' type: '{type(id)}'")

        requested_at = request.state.requested_at
        if not isinstance(requested_at, datetime):
            raise ValueError(f"Invalid 'requested_at' type: '{type(requested_at)}'")

        ip_address = extract_client_ip(request)

        user_agent_string = request.headers.get("user-agent", "")
        user_agent = UserAgent.from_string(user_agent_string=user_agent_string)

        return cls(
            id=id,
            requested_at=requested_at,
            method=request.method,
            url=request.url.path,
            ip_address=ip_address,
            is_internal=(
                None
                if ip_address == "unknown"
                else (
                    ip_address.startswith("10.")
                    or ip_address.startswith("192.168.")
                    or ip_address.startswith("172.")
                )
            ),
            headers=request.headers.items(),
            path_params=None if not request.path_params else request.path_params,
            query_params=(
                None if not request.query_params else str(request.query_params)
            ),
            user_agent=user_agent,
            referer=request.headers.get("referer"),
            origin=request.headers.get("origin"),
            host=request.headers.get("host"),
            forwarded_proto=request.headers.get("x-forwarded-proto"),
            language=request.headers.get("accept-language"),
        )

    @classmethod
    def as_dependency(cls):
        """Create a FastAPI dependency for this request context."""

        def dependency(request: Request) -> "RequestContext":
            return cls.from_request(request)

        return dependency


GenericRequestContextT = TypeVar(
    "GenericRequestContextT", bound=Optional[RequestContext]
)


class RequestContextMixin(BaseModel, Generic[GenericRequestContextT]):
    request_context: GenericRequestContextT = Field(
        ..., description="Request's context"
    )
