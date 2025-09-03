from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from maleo.mixins.general import Key, Name
from maleo.types.base.dict import OptionalStringToAnyDict
from maleo.types.base.string import OptionalString


class UrlSlug(BaseModel):
    url_slug: OptionalString = Field(None, description="URL Slug")


class ResourceIdentifier(Name, Key, UrlSlug):
    pass


class Resource(BaseModel):
    identifiers: List[ResourceIdentifier] = Field(
        ..., min_length=1, description="Identifiers"
    )
    details: OptionalStringToAnyDict = Field(None, description="Details")

    def aggregate(self, sep: str = ":") -> str:
        return sep.join([id.key for id in self.identifiers])


ResourceT = TypeVar("ResourceT", bound=Optional[Resource])


class ResourceMixin(BaseModel, Generic[ResourceT]):
    resource: ResourceT = Field(..., description="Resource")
