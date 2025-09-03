from datetime import datetime
from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from uuid import UUID
from maleo.enums.status import DataStatus as DataStatusEnum
from maleo.mixins.timestamp import (
    CreationTimestamp,
    UpdateTimestamp,
    DeletionTimestamp,
    RestorationTimestamp,
    DeactivationTimestamp,
    ActivationTimestamp,
)
from maleo.types.base.datetime import OptionalDatetime


class DataIdentifier(BaseModel):
    id: int = Field(..., ge=1, description="Data's ID, must be >= 1.")
    uuid: UUID = Field(..., description="Data's UUID.")


class DataStatus(BaseModel):
    status: DataStatusEnum = Field(..., description="Data's status")


class DataLifecycleTimestamp(UpdateTimestamp, CreationTimestamp):
    pass


class DataStatusTimestamp(
    DeletionTimestamp[OptionalDatetime],
    RestorationTimestamp[OptionalDatetime],
    DeactivationTimestamp[OptionalDatetime],
    ActivationTimestamp[datetime],
):
    pass


class DataTimestamp(DataStatusTimestamp, DataLifecycleTimestamp):
    pass


OldDataT = TypeVar("OldDataT")
NewDataT = TypeVar("NewDataT")


class DataPair(BaseModel, Generic[OldDataT, NewDataT]):
    old: OldDataT = Field(..., description="Old data")
    new: NewDataT = Field(..., description="New data")


GenericDataT = TypeVar("GenericDataT")


class DataMixin(BaseModel, Generic[GenericDataT]):
    data: GenericDataT = Field(..., description="Data.")


DataT = TypeVar("DataT", bound=BaseModel)
