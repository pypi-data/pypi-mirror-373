from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from maleo.enums.operation import (
    Origin as OriginEnum,
    Layer as LayerEnum,
    Target as TargetEnum,
)
from maleo.types.base.dict import OptionalStringToAnyDict


T = TypeVar("T", bound=StrEnum)


class OperationContextComponent(BaseModel, Generic[T]):
    type: T = Field(..., description="Component's type")
    details: OptionalStringToAnyDict = Field(None, description="Component's details")


class OperationOrigin(OperationContextComponent[OriginEnum]):
    pass


class OperationOriginMixin(BaseModel):
    origin: OperationOrigin = Field(..., description="Operation's origin")


class OperationLayer(OperationContextComponent[LayerEnum]):
    pass


class OperationLayerMixin(BaseModel):
    layer: OperationLayer = Field(..., description="Operation's layer")


class OperationTarget(OperationContextComponent[TargetEnum]):
    pass


class OperationTargetMixin(BaseModel):
    target: OperationTarget = Field(..., description="Operation's target")


class OperationContext(OperationTargetMixin, OperationLayerMixin, OperationOriginMixin):
    pass


OperationContextT = TypeVar("OperationContextT", bound=Optional[OperationContext])


UTILITY_OPERATION_CONTEXT = OperationContext(
    origin=OperationOrigin(type=OriginEnum.UTILITY, details=None),
    layer=OperationLayer(type=LayerEnum.INTERNAL, details=None),
    target=OperationTarget(type=TargetEnum.INTERNAL, details=None),
)


def generate_operation_context(
    origin: OriginEnum,
    layer: LayerEnum,
    target: TargetEnum = TargetEnum.INTERNAL,
    origin_details: OptionalStringToAnyDict = None,
    layer_details: OptionalStringToAnyDict = None,
    target_details: OptionalStringToAnyDict = None,
) -> OperationContext:
    return OperationContext(
        origin=OperationOrigin(type=origin, details=origin_details),
        layer=OperationLayer(type=layer, details=layer_details),
        target=OperationTarget(type=target, details=target_details),
    )


class OperationContextMixin(BaseModel, Generic[OperationContextT]):
    context: OperationContextT = Field(..., description="Operation's context")
