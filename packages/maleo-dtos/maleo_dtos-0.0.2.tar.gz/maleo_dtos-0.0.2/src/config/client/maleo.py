from pydantic import BaseModel, Field
from typing import Optional, TypeVar
from maleo.enums.environment import Environment
from maleo.enums.service import Key


class MaleoClientConfig(BaseModel):
    environment: Environment = Field(..., description="Client's environment")
    key: Key = Field(..., description="Client's key")
    name: str = Field(..., description="Client's name")
    url: str = Field(..., description="Client's URL")


class MaleoTelemetryClientConfigMixin(BaseModel):
    telemetry: MaleoClientConfig = Field(
        ..., description="MaleoTelemetry client's configuration"
    )


class MaleoMetadataClientConfigMixin(BaseModel):
    metadata: MaleoClientConfig = Field(
        ..., description="MaleoMetadata client's configuration"
    )


class MaleoIdentityClientConfigMixin(BaseModel):
    identity: MaleoClientConfig = Field(
        ..., description="MaleoIdentity client's configuration"
    )


class MaleoAccessClientConfigMixin(BaseModel):
    access: MaleoClientConfig = Field(
        ..., description="MaleoAccess client's configuration"
    )


class MaleoWorkshopClientConfigMixin(BaseModel):
    workshop: MaleoClientConfig = Field(
        ..., description="MaleoWorkshop client's configuration"
    )


class MaleoResearchClientConfigMixin(BaseModel):
    research: MaleoClientConfig = Field(
        ..., description="MaleoResearch client's configuration"
    )


class MaleoSOAPIEClientConfigMixin(BaseModel):
    soapie: MaleoClientConfig = Field(
        ..., description="MaleoSOAPIE client's configuration"
    )


class MaleoMedixClientConfigMixin(BaseModel):
    medix: MaleoClientConfig = Field(
        ..., description="MaleoMedix client's configuration"
    )


class MaleoDICOMClientConfigMixin(BaseModel):
    dicom: MaleoClientConfig = Field(
        ..., description="MaleoDICOM client's configuration"
    )


class MaleoScribeClientConfigMixin(BaseModel):
    scribe: MaleoClientConfig = Field(
        ..., description="MaleoScribe client's configuration"
    )


class MaleoCDSClientConfigMixin(BaseModel):
    cds: MaleoClientConfig = Field(..., description="MaleoCDS client's configuration")


class MaleoImagingClientConfigMixin(BaseModel):
    imaging: MaleoClientConfig = Field(
        ..., description="MaleoImaging client's configuration"
    )


class MaleoMCUClientConfigMixin(BaseModel):
    mcu: MaleoClientConfig = Field(..., description="MaleoMCU client's configuration")


class MaleoClientsConfig(BaseModel):
    pass


MaleoClientsConfigT = TypeVar("MaleoClientsConfigT", bound=Optional[MaleoClientsConfig])
