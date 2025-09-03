from pydantic import BaseModel, Field
from .resource import ResourceConfig


class SystemConfig(BaseModel):
    resource: ResourceConfig = Field(..., description="Resource configuration")
