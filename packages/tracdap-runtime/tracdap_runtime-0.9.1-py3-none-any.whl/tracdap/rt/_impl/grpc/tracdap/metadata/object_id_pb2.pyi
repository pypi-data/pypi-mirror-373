from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObjectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OBJECT_TYPE_NOT_SET: _ClassVar[ObjectType]
    DATA: _ClassVar[ObjectType]
    MODEL: _ClassVar[ObjectType]
    FLOW: _ClassVar[ObjectType]
    JOB: _ClassVar[ObjectType]
    FILE: _ClassVar[ObjectType]
    CUSTOM: _ClassVar[ObjectType]
    STORAGE: _ClassVar[ObjectType]
    SCHEMA: _ClassVar[ObjectType]
    RESULT: _ClassVar[ObjectType]
    CONFIG: _ClassVar[ObjectType]
    RESOURCE: _ClassVar[ObjectType]
OBJECT_TYPE_NOT_SET: ObjectType
DATA: ObjectType
MODEL: ObjectType
FLOW: ObjectType
JOB: ObjectType
FILE: ObjectType
CUSTOM: ObjectType
STORAGE: ObjectType
SCHEMA: ObjectType
RESULT: ObjectType
CONFIG: ObjectType
RESOURCE: ObjectType

class TagHeader(_message.Message):
    __slots__ = ("objectType", "objectId", "objectVersion", "objectTimestamp", "tagVersion", "tagTimestamp", "isLatestObject", "isLatestTag")
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECTID_FIELD_NUMBER: _ClassVar[int]
    OBJECTVERSION_FIELD_NUMBER: _ClassVar[int]
    OBJECTTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TAGVERSION_FIELD_NUMBER: _ClassVar[int]
    TAGTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ISLATESTOBJECT_FIELD_NUMBER: _ClassVar[int]
    ISLATESTTAG_FIELD_NUMBER: _ClassVar[int]
    objectType: ObjectType
    objectId: str
    objectVersion: int
    objectTimestamp: _type_pb2.DatetimeValue
    tagVersion: int
    tagTimestamp: _type_pb2.DatetimeValue
    isLatestObject: bool
    isLatestTag: bool
    def __init__(self, objectType: _Optional[_Union[ObjectType, str]] = ..., objectId: _Optional[str] = ..., objectVersion: _Optional[int] = ..., objectTimestamp: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., tagVersion: _Optional[int] = ..., tagTimestamp: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., isLatestObject: bool = ..., isLatestTag: bool = ...) -> None: ...

class TagSelector(_message.Message):
    __slots__ = ("objectType", "objectId", "latestObject", "objectVersion", "objectAsOf", "latestTag", "tagVersion", "tagAsOf")
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECTID_FIELD_NUMBER: _ClassVar[int]
    LATESTOBJECT_FIELD_NUMBER: _ClassVar[int]
    OBJECTVERSION_FIELD_NUMBER: _ClassVar[int]
    OBJECTASOF_FIELD_NUMBER: _ClassVar[int]
    LATESTTAG_FIELD_NUMBER: _ClassVar[int]
    TAGVERSION_FIELD_NUMBER: _ClassVar[int]
    TAGASOF_FIELD_NUMBER: _ClassVar[int]
    objectType: ObjectType
    objectId: str
    latestObject: bool
    objectVersion: int
    objectAsOf: _type_pb2.DatetimeValue
    latestTag: bool
    tagVersion: int
    tagAsOf: _type_pb2.DatetimeValue
    def __init__(self, objectType: _Optional[_Union[ObjectType, str]] = ..., objectId: _Optional[str] = ..., latestObject: bool = ..., objectVersion: _Optional[int] = ..., objectAsOf: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., latestTag: bool = ..., tagVersion: _Optional[int] = ..., tagAsOf: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ...) -> None: ...
