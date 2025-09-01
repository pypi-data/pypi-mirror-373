from google.oauth2.service_account import Credentials
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class MaleoCredential(BaseModel):
    id: int = Field(..., description="ID")
    uuid: UUID = Field(..., description="UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class Credential(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    google: Credentials = Field(..., description="Google credentials")
    maleo: MaleoCredential = Field(..., description="Maleo credentials")
