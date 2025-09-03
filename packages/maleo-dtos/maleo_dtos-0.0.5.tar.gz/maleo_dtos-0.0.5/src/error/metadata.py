from pydantic import BaseModel, Field
from maleo.types.base.any import OptionalAny
from maleo.types.base.string import OptionalListOfStrings


class ErrorMetadata(BaseModel):
    details: OptionalAny = Field(None, description="Details")
    traceback: OptionalListOfStrings = Field(None, description="Traceback")
