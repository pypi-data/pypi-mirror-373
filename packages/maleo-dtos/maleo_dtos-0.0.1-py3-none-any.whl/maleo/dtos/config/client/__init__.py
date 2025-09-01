from pydantic import BaseModel, Field
from typing import Generic, Optional
from .maleo import MaleoClientsConfigT


class ClientConfig(BaseModel, Generic[MaleoClientsConfigT]):
    maleo: Optional[MaleoClientsConfigT] = Field(
        None,
        description="Maleo client's configurations",
    )
