from pydantic import BaseModel, Field
from typing import Generic, TypeVar


class TopicConfig(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="database-operation")
DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="request-operation")
DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="resource-operation")
DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="system-operation")
DEFAULT_OPERATION_TOPIC_CONFIGURATION = TopicConfig(id="operation")
DEFAULT_RESOURCE_USAGE_TOPIC_CONFIGURATION = TopicConfig(id="resource-usage")


class TopicsConfig(BaseModel):
    database_operation: TopicConfig = Field(
        default=DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATION,
        description="Database operation topic configurations",
    )
    request_operation: TopicConfig = Field(
        default=DEFAULT_REQUEST_OPERATION_TOPIC_CONFIGURATION,
        description="Request operation topic configurations",
    )
    resource_operation: TopicConfig = Field(
        default=DEFAULT_RESOURCE_OPERATION_TOPIC_CONFIGURATION,
        description="Resource operation topic configurations",
    )
    system_operation: TopicConfig = Field(
        default=DEFAULT_SYSTEM_OPERATION_TOPIC_CONFIGURATION,
        description="System operation topic configurations",
    )
    operation: TopicConfig = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATION,
        description="Operation topic configurations",
    )
    resource_usage: TopicConfig = Field(
        default=DEFAULT_RESOURCE_USAGE_TOPIC_CONFIGURATION,
        description="Resource usage topic configurations",
    )


TopicsConfigT = TypeVar("TopicsConfigT", bound=TopicsConfig)


class PublisherConfig(BaseModel, Generic[TopicsConfigT]):
    topics: TopicsConfigT = Field(..., description="Topics configurations")
