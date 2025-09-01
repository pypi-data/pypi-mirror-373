from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CustomDefinition(_message.Message):
    __slots__ = ("customSchemaType", "customSchemaVersion", "customData")
    CUSTOMSCHEMATYPE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMSCHEMAVERSION_FIELD_NUMBER: _ClassVar[int]
    CUSTOMDATA_FIELD_NUMBER: _ClassVar[int]
    customSchemaType: str
    customSchemaVersion: int
    customData: bytes
    def __init__(self, customSchemaType: _Optional[str] = ..., customSchemaVersion: _Optional[int] = ..., customData: _Optional[bytes] = ...) -> None: ...
