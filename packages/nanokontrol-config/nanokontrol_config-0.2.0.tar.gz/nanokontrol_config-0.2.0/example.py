from pydantic import BaseModel, model_validator
from enum import Enum, auto


class Generic(BaseModel):
    class Type(Enum):
        DEVICE_INQUIRY_REQUEST = auto()
        DEVICE_INQUIRY_REPLY = auto()

    common: int


class Special(Generic):
    class Type(Enum):
        DATA_SENT = auto()
        DATA_RECEIVED = auto()

    preprocessed: bytes

    @model_validator(mode="before")
    def translate_fields(
        cls, values: dict[str, str | bytes]
    ) -> dict[str, str | bytes]:
        return {
            "common": values["common"],
            "preprocessed": values["payload"] * 2,
        }


s = Special(common=42, payload=b"abc")
v = Generic.Type.DEVICE_INQUIRY_REPLY
print(v)
