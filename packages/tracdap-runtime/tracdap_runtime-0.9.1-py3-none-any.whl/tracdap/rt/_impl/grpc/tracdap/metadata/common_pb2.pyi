from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class MetadataFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METADATA_FORMAT_NOT_SET: _ClassVar[MetadataFormat]
    PROTO: _ClassVar[MetadataFormat]
    JSON: _ClassVar[MetadataFormat]
    YAML: _ClassVar[MetadataFormat]

class MetadataVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METADATA_VERSION_NOT_SET: _ClassVar[MetadataVersion]
    V1: _ClassVar[MetadataVersion]
    CURRENT: _ClassVar[MetadataVersion]
METADATA_FORMAT_NOT_SET: MetadataFormat
PROTO: MetadataFormat
JSON: MetadataFormat
YAML: MetadataFormat
METADATA_VERSION_NOT_SET: MetadataVersion
V1: MetadataVersion
CURRENT: MetadataVersion

class TenantInfo(_message.Message):
    __slots__ = ("tenantCode", "description")
    TENANTCODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    tenantCode: str
    description: str
    def __init__(self, tenantCode: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
