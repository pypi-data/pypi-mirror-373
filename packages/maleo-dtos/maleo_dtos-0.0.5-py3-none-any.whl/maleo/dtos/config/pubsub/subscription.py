from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, Optional, TypeVar
from maleo.types.controllers.message import ReturnT, MessageController


class SubscriptionConfig(BaseModel):
    id: str = Field(..., description="Subscription's ID")
    max_messages: int = Field(10, description="Subscription's Max messages")
    ack_deadline: int = Field(10, description="Subscription's ACK deadline")


class ExtendedSubscriptionConfig(SubscriptionConfig, Generic[ReturnT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    controller: Optional[MessageController[ReturnT]] = Field(
        None, description="Optional message controller"
    )


SubscriptionsConfigT = TypeVar("SubscriptionsConfigT", bound=Optional[BaseModel])
