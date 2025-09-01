from pydantic import BaseModel, Field
from maleo.constants.middleware import (
    DEFAULT_ALLOW_METHODS,
    DEFAULT_ALLOW_HEADERS,
    DEFAULT_EXPOSE_HEADERS,
)
from maleo.types.base.string import SequenceOfStrings


class CORSMiddlewareConfig(BaseModel):
    allow_origins: SequenceOfStrings = Field(
        default_factory=list, description="Allowed origins"
    )
    allow_methods: SequenceOfStrings = Field(
        DEFAULT_ALLOW_METHODS, description="Allowed methods"
    )
    allow_headers: SequenceOfStrings = Field(
        DEFAULT_ALLOW_HEADERS, description="Allowed headers"
    )
    allow_credentials: bool = Field(True, description="Allowed credentials")
    expose_headers: SequenceOfStrings = Field(
        DEFAULT_EXPOSE_HEADERS, description="Exposed headers"
    )


class RateLimiterConfig(BaseModel):
    limit: int = Field(10, description="Request limit (per 'window' seconds)")
    window: int = Field(1, description="Request limit window (seconds)")
    cleanup_interval: int = Field(
        60, description="Interval for middleware cleanup (seconds)"
    )
    idle_timeout: int = Field(300, description="Idle timeout (seconds)")


class MiddlewareConfig(BaseModel):
    cors: CORSMiddlewareConfig = Field(
        ..., description="CORS middleware's configurations"
    )
    rate_limiter: RateLimiterConfig = Field(
        ..., description="Rate limiter's configurations"
    )
