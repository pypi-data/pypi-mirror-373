from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Union

T = TypeVar("T", bound=Union[bytes, str])


class Secret(BaseModel, Generic[T]):
    name: str = Field(..., description="Secret's name")
    version: str = Field("latest", description="Secret's version")
    value: T = Field(..., description="Secret's value")
