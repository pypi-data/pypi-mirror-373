from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESOURCE_TYPE_NOT_SET: _ClassVar[ResourceType]
    MODEL_REPOSITORY: _ClassVar[ResourceType]
    INTERNAL_STORAGE: _ClassVar[ResourceType]
    EXTERNAL_STORAGE: _ClassVar[ResourceType]
RESOURCE_TYPE_NOT_SET: ResourceType
MODEL_REPOSITORY: ResourceType
INTERNAL_STORAGE: ResourceType
EXTERNAL_STORAGE: ResourceType

class ResourceDefinition(_message.Message):
    __slots__ = ("resourceType", "protocol", "subProtocol", "publicProperties", "properties", "secrets")
    class PublicPropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SecretsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RESOURCETYPE_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    SUBPROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PUBLICPROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    resourceType: ResourceType
    protocol: str
    subProtocol: str
    publicProperties: _containers.ScalarMap[str, str]
    properties: _containers.ScalarMap[str, str]
    secrets: _containers.ScalarMap[str, str]
    def __init__(self, resourceType: _Optional[_Union[ResourceType, str]] = ..., protocol: _Optional[str] = ..., subProtocol: _Optional[str] = ..., publicProperties: _Optional[_Mapping[str, str]] = ..., properties: _Optional[_Mapping[str, str]] = ..., secrets: _Optional[_Mapping[str, str]] = ...) -> None: ...
