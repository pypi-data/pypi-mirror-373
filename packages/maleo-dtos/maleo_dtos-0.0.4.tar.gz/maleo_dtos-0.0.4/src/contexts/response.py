import json
from base64 import b64decode, b64encode
from charset_normalizer import from_bytes
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    ValidationInfo,
)
from typing import Generic, List, Optional, Tuple, TypeVar, Union
from maleo.types.base.dict import StringToAnyDict
from maleo.types.base.string import OptionalString


class ResponseContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status_code: int = Field(..., description="Status code")
    media_type: OptionalString = Field(None, description="Media type (Optional)")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )
    body: Union[bytes, memoryview] = Field(..., description="Content (Optional)")

    @field_serializer("body")
    def serialize_body(
        self, body: Union[bytes, memoryview]
    ) -> Union[StringToAnyDict, str]:
        """Serialize body for logging (JSON, text/* with encoding detection, or Base64 fallback)."""
        try:
            raw_bytes = bytes(body)

            # JSON case (assume UTF-8 as per RFC 8259)
            if self.media_type and "application/json" in self.media_type.lower():
                try:
                    return json.loads(raw_bytes.decode("utf-8"))
                except Exception:
                    return raw_bytes.decode("utf-8", errors="replace")

            # Text case (auto-detect encoding, covers text/html, text/plain, etc.)
            elif self.media_type and self.media_type.lower().startswith("text/"):
                detected = from_bytes(raw_bytes).best()
                return (
                    str(detected)
                    if detected
                    else raw_bytes.decode("utf-8", errors="replace")
                )

            # Unknown type → base64 encode to preserve safely
            else:
                return b64encode(raw_bytes).decode("ascii")

        except Exception as e:
            # Fallback for logging safety
            return f"<unserializable body: {str(e)}>"

    @field_validator("body", mode="before")
    def deserialize_body(cls, v, info: ValidationInfo):
        """Inverse of serialize_body: turn incoming value back into bytes."""
        media_type: OptionalString = info.data.get("media_type", None)

        # Already bytes or memoryview — nothing to do
        if isinstance(v, (bytes, memoryview)):
            return v

        # JSON case
        if media_type and "application/json" in media_type.lower():
            if isinstance(v, dict):
                return json.dumps(v).encode("utf-8")
            elif isinstance(v, str):
                return v.encode("utf-8")
            else:
                raise ValueError("Invalid JSON body type")

        # Text case
        if media_type and media_type.lower().startswith("text/"):
            if isinstance(v, str):
                return v.encode("utf-8")
            else:
                raise ValueError("Invalid text body type")

        # Fallback: base64
        if isinstance(v, str):
            try:
                return b64decode(v)
            except Exception:
                raise ValueError("Invalid Base64 body string")

        raise ValueError("Unsupported body type")


ResponseContextT = TypeVar("ResponseContextT", bound=Optional[ResponseContext])


class ResponseContextMixin(BaseModel, Generic[ResponseContextT]):
    response_context: ResponseContextT = Field(..., description="Response's context")
