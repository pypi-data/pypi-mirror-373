from pydantic import BaseModel, Field
from typing import Generic, Optional
from .publisher import TopicsConfigT, PublisherConfig
from .subscription import SubscriptionsConfigT


class PubSubConfig(BaseModel, Generic[TopicsConfigT, SubscriptionsConfigT]):
    publisher: PublisherConfig[TopicsConfigT] = Field(
        ...,
        description="Publisher's configurations",
    )
    subscriptions: Optional[SubscriptionsConfigT] = Field(
        None, description="Subscriptions's configurations"
    )
