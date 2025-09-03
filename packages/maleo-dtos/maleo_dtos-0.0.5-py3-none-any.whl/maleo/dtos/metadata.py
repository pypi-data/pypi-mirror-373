from pydantic import BaseModel, Field
from typing import Dict, Generic, Optional, TypeVar, Union
from maleo.mixins.general import Success, Descriptor, OptionalOther


MetadataT = TypeVar("MetadataT", bound=Optional[BaseModel])


class MetadataMixin(BaseModel, Generic[MetadataT]):
    metadata: MetadataT = Field(..., description="Metadata")


class FieldExpansionMetadata(OptionalOther, Descriptor[str], Success[bool]):
    pass


class FieldExpansionMetadataMixin(BaseModel):
    field_expansion: Optional[Union[str, Dict[str, FieldExpansionMetadata]]] = Field(
        None, description="Field expansion metadata"
    )
