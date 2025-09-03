from pydantic import BaseModel, Field


class Object(BaseModel):
    url: str = Field(..., description="File's URL")
