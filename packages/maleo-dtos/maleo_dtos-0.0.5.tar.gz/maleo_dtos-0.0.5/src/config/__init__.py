from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, TypeVar
from .client import ClientConfig
from .client.maleo import MaleoClientsConfigT
from .database import DatabaseConfigT
from .middleware import MiddlewareConfig
from .pubsub import PubSubConfig
from .pubsub.publisher import TopicsConfigT
from .pubsub.subscription import SubscriptionsConfigT
from .system import SystemConfig


class Config(
    BaseModel,
    Generic[
        MaleoClientsConfigT,
        DatabaseConfigT,
        TopicsConfigT,
        SubscriptionsConfigT,
    ],
):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client: ClientConfig[MaleoClientsConfigT] = Field(
        ..., description="Client's configurations"
    )
    database: DatabaseConfigT = Field(..., description="Database's configurations")
    middleware: MiddlewareConfig = Field(..., description="Middleware's configurations")
    pubsub: PubSubConfig[
        TopicsConfigT,
        SubscriptionsConfigT,
    ] = Field(..., description="PubSub's configurations")
    system: SystemConfig = Field(..., description="System's configurations")


ConfigT = TypeVar("ConfigT", bound=Config)
