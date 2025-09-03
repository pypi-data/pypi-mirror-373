from pydantic import BaseModel
from typing import Optional, TypeVar


class DatabaseConfig(BaseModel):
    pass


DatabaseConfigT = TypeVar("DatabaseConfigT", bound=Optional[DatabaseConfig])
