from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from .data import DataPair, GenericDataT, DataMixin, DataT
from .pagination import GenericPaginationT, PaginationT, PaginationMixin
from .metadata import MetadataMixin, MetadataT
from maleo.mixins.general import OptionalOther


class Payload(
    OptionalOther,
    MetadataMixin[MetadataT],
    PaginationMixin[GenericPaginationT],
    DataMixin[GenericDataT],
    BaseModel,
    Generic[GenericDataT, GenericPaginationT, MetadataT],
):
    pass


PayloadT = TypeVar("PayloadT", bound=Payload)


class PayloadMixin(BaseModel, Generic[PayloadT]):
    payload: PayloadT = Field(..., description="Payloaf")


class NoDataPayload(
    Payload[None, None, MetadataT],
    Generic[MetadataT],
):
    data: None = None
    pagination: None = None


class SingleDataPayload(
    Payload[DataT, None, MetadataT],
    Generic[DataT, MetadataT],
):
    pagination: None = None


class CreateSingleDataPayload(
    Payload[DataPair[None, DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class ReadSingleDataPayload(
    Payload[DataPair[DataT, None], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class UpdateSingleDataPayload(
    Payload[DataPair[DataT, DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class DeleteSingleDataPayload(
    Payload[DataPair[DataT, None], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pass


class OptionalSingleDataPayload(
    Payload[Optional[DataT], None, MetadataT],
    Generic[DataT, MetadataT],
):
    pagination: None = None


class MultipleDataPayload(
    Payload[List[DataT], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class CreateMultipleDataPayload(
    Payload[DataPair[None, List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class ReadMultipleDataPayload(
    Payload[DataPair[List[DataT], None], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class UpdateMultipleDataPayload(
    Payload[DataPair[List[DataT], List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class DeleteMultipleDataPayload(
    Payload[DataPair[List[DataT], None], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass


class OptionalMultipleDataPayload(
    Payload[Optional[List[DataT]], PaginationT, MetadataT],
    Generic[DataT, PaginationT, MetadataT],
):
    pass
