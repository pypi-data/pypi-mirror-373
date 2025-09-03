from pydantic import BaseModel, Field


class CPUUsage(BaseModel):
    raw: float = Field(..., ge=0.0, le=100.0, description="Raw CPU Usage (%)")
    smooth: float = Field(..., ge=0.0, le=100.0, description="Smooth CPU Usage (%)")


class ResourceUsage(BaseModel):
    cpu: CPUUsage = Field(..., description="CPU Usage")
    memory: float = Field(..., ge=0.0, description="Memory Usage (MB)")
