from pydantic import BaseModel, Field
from typing import Optional, Tuple
from user_agents.parsers import parse


class Browser(BaseModel):
    family: str
    version: Tuple[int, ...]
    version_string: str


class OperatingSystem(BaseModel):
    family: str
    version: Tuple[int, ...]
    version_string: str


class Device(BaseModel):
    family: str
    brand: Optional[str] = None
    model: Optional[str] = None


class UserAgent(BaseModel):
    ua_string: str = Field(..., description="Raw User-Agent header")
    browser: Browser = Field(..., description="Browser User-Agent")
    os: OperatingSystem = Field(..., description="OS User-Agent")
    device: Device = Field(..., description="Platform User-Agent")

    is_mobile: bool
    is_tablet: bool
    is_pc: bool
    is_bot: bool
    is_touch_capable: bool
    is_email_client: bool

    @classmethod
    def from_string(cls, user_agent_string: str) -> "UserAgent":
        parsed_user_agent = parse(user_agent_string)
        return cls.model_validate(parsed_user_agent, from_attributes=True)
