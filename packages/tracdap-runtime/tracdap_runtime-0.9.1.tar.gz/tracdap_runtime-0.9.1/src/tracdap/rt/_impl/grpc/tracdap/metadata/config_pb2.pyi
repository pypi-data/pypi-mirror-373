from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import resource_pb2 as _resource_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONFIG_TYPE_NOT_SET: _ClassVar[ConfigType]
    PROPERTIES: _ClassVar[ConfigType]
CONFIG_TYPE_NOT_SET: ConfigType
PROPERTIES: ConfigType

class ConfigEntry(_message.Message):
    __slots__ = ("configClass", "configKey", "configVersion", "configTimestamp", "isLatestConfig", "configDeleted", "details")
    CONFIGCLASS_FIELD_NUMBER: _ClassVar[int]
    CONFIGKEY_FIELD_NUMBER: _ClassVar[int]
    CONFIGVERSION_FIELD_NUMBER: _ClassVar[int]
    CONFIGTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ISLATESTCONFIG_FIELD_NUMBER: _ClassVar[int]
    CONFIGDELETED_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    configClass: str
    configKey: str
    configVersion: int
    configTimestamp: _type_pb2.DatetimeValue
    isLatestConfig: bool
    configDeleted: bool
    details: ConfigDetails
    def __init__(self, configClass: _Optional[str] = ..., configKey: _Optional[str] = ..., configVersion: _Optional[int] = ..., configTimestamp: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., isLatestConfig: bool = ..., configDeleted: bool = ..., details: _Optional[_Union[ConfigDetails, _Mapping]] = ...) -> None: ...

class ConfigDetails(_message.Message):
    __slots__ = ("objectSelector", "objectType", "configType", "resourceType")
    OBJECTSELECTOR_FIELD_NUMBER: _ClassVar[int]
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    CONFIGTYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCETYPE_FIELD_NUMBER: _ClassVar[int]
    objectSelector: _object_id_pb2.TagSelector
    objectType: _object_id_pb2.ObjectType
    configType: ConfigType
    resourceType: _resource_pb2.ResourceType
    def __init__(self, objectSelector: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., objectType: _Optional[_Union[_object_id_pb2.ObjectType, str]] = ..., configType: _Optional[_Union[ConfigType, str]] = ..., resourceType: _Optional[_Union[_resource_pb2.ResourceType, str]] = ...) -> None: ...

class ConfigDefinition(_message.Message):
    __slots__ = ("configType", "properties")
    class PropertiesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CONFIGTYPE_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    configType: ConfigType
    properties: _containers.ScalarMap[str, str]
    def __init__(self, configType: _Optional[_Union[ConfigType, str]] = ..., properties: _Optional[_Mapping[str, str]] = ...) -> None: ...
