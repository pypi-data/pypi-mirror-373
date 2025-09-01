from pydantic import BaseModel, Field


class ResourceUsageConfig(BaseModel):
    interval: float = Field(5.0, ge=5.0, description="Monitor interval")
    window: int = Field(5, ge=5, description="Smoothing window")


class ResourceLimitConfig(BaseModel):
    cpu: float = Field(
        90.0,
        ge=0.0,
        le=100.0,
        description="CPU usage threshold (%) applied to smoothed CPU value",
    )
    memory: float = Field(2048.0, ge=0.0, description="Memory usage threshold (MB)")


class ResourceConfig(BaseModel):
    usage: ResourceUsageConfig = Field(..., description="Resource usage configuration")
    limit: ResourceLimitConfig = Field(..., description="Resource limit configuration")
