from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import Self
from maleo.enums.environment import Environment
from maleo.enums.execution import ApplicationExecution
from maleo.enums.service import Key, Name
from maleo.types.base.string import OptionalString


class ServiceSettings(BaseSettings):
    EXECUTION: ApplicationExecution = Field(
        ApplicationExecution.CONTAINER, description="Application's execution mode"
    )
    ENVIRONMENT: Environment = Field(..., description="Environment")
    HOST: str = Field("127.0.0.1", description="Application's host")
    PORT: int = Field(8000, description="Application's port")
    HOST_PORT: int = Field(8000, description="Host's port")
    DOCKER_NETWORK: str = Field("maleo-suite", description="Docker's network")
    SERVICE_KEY: Key = Field(..., description="Service's key")
    SERVICE_NAME: Name = Field(..., description="Service's name")
    ROOT_PATH: str = Field("", description="Application's root path")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        "/etc/maleo/credentials/google-service-account.json",
        description="Google application credential's file path",
    )
    USE_LOCAL_CONFIGURATIONS: bool = Field(
        False, description="Whether to use local configurations"
    )
    CONFIGURATIONS_PATH: OptionalString = Field(None, description="Configurations path")
    KEY_PASSWORD: OptionalString = Field(None, description="Key's password")
    PRIVATE_KEY: OptionalString = Field(None, description="Private key")
    PUBLIC_KEY: OptionalString = Field(None, description="Public key")

    @model_validator(mode="after")
    def validate_configurations_path(self) -> Self:
        if self.USE_LOCAL_CONFIGURATIONS:
            if self.CONFIGURATIONS_PATH is None:
                self.CONFIGURATIONS_PATH = f"/etc/maleo/configurations/{self.SERVICE_KEY}/{self.ENVIRONMENT}.yaml"
            configurations_path = Path(self.CONFIGURATIONS_PATH)
            if not configurations_path.exists() or not configurations_path.is_file():
                raise ValueError(
                    f"Configurations path '{self.CONFIGURATIONS_PATH}' either did not exist or is not a file"
                )

        return self
