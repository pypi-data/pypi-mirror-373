from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CopyStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COPY_STATUS_NOT_SET: _ClassVar[CopyStatus]
    COPY_AVAILABLE: _ClassVar[CopyStatus]
    COPY_EXPUNGED: _ClassVar[CopyStatus]

class IncarnationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INCARNATION_STATUS_NOT_SET: _ClassVar[IncarnationStatus]
    INCARNATION_AVAILABLE: _ClassVar[IncarnationStatus]
    INCARNATION_EXPUNGED: _ClassVar[IncarnationStatus]

class StorageLayout(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OBJECT_ID_LAYOUT: _ClassVar[StorageLayout]
    DEVELOPER_LAYOUT: _ClassVar[StorageLayout]
COPY_STATUS_NOT_SET: CopyStatus
COPY_AVAILABLE: CopyStatus
COPY_EXPUNGED: CopyStatus
INCARNATION_STATUS_NOT_SET: IncarnationStatus
INCARNATION_AVAILABLE: IncarnationStatus
INCARNATION_EXPUNGED: IncarnationStatus
OBJECT_ID_LAYOUT: StorageLayout
DEVELOPER_LAYOUT: StorageLayout

class StorageCopy(_message.Message):
    __slots__ = ("storageKey", "storagePath", "storageFormat", "copyStatus", "copyTimestamp", "storageOptions")
    class StorageOptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    STORAGEKEY_FIELD_NUMBER: _ClassVar[int]
    STORAGEPATH_FIELD_NUMBER: _ClassVar[int]
    STORAGEFORMAT_FIELD_NUMBER: _ClassVar[int]
    COPYSTATUS_FIELD_NUMBER: _ClassVar[int]
    COPYTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STORAGEOPTIONS_FIELD_NUMBER: _ClassVar[int]
    storageKey: str
    storagePath: str
    storageFormat: str
    copyStatus: CopyStatus
    copyTimestamp: _type_pb2.DatetimeValue
    storageOptions: _containers.MessageMap[str, _type_pb2.Value]
    def __init__(self, storageKey: _Optional[str] = ..., storagePath: _Optional[str] = ..., storageFormat: _Optional[str] = ..., copyStatus: _Optional[_Union[CopyStatus, str]] = ..., copyTimestamp: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., storageOptions: _Optional[_Mapping[str, _type_pb2.Value]] = ...) -> None: ...

class StorageIncarnation(_message.Message):
    __slots__ = ("copies", "incarnationIndex", "incarnationTimestamp", "incarnationStatus")
    COPIES_FIELD_NUMBER: _ClassVar[int]
    INCARNATIONINDEX_FIELD_NUMBER: _ClassVar[int]
    INCARNATIONTIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INCARNATIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    copies: _containers.RepeatedCompositeFieldContainer[StorageCopy]
    incarnationIndex: int
    incarnationTimestamp: _type_pb2.DatetimeValue
    incarnationStatus: IncarnationStatus
    def __init__(self, copies: _Optional[_Iterable[_Union[StorageCopy, _Mapping]]] = ..., incarnationIndex: _Optional[int] = ..., incarnationTimestamp: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., incarnationStatus: _Optional[_Union[IncarnationStatus, str]] = ...) -> None: ...

class StorageItem(_message.Message):
    __slots__ = ("incarnations",)
    INCARNATIONS_FIELD_NUMBER: _ClassVar[int]
    incarnations: _containers.RepeatedCompositeFieldContainer[StorageIncarnation]
    def __init__(self, incarnations: _Optional[_Iterable[_Union[StorageIncarnation, _Mapping]]] = ...) -> None: ...

class StorageDefinition(_message.Message):
    __slots__ = ("dataItems", "storageOptions", "layout")
    class DataItemsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: StorageItem
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[StorageItem, _Mapping]] = ...) -> None: ...
    class StorageOptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    DATAITEMS_FIELD_NUMBER: _ClassVar[int]
    STORAGEOPTIONS_FIELD_NUMBER: _ClassVar[int]
    LAYOUT_FIELD_NUMBER: _ClassVar[int]
    dataItems: _containers.MessageMap[str, StorageItem]
    storageOptions: _containers.MessageMap[str, _type_pb2.Value]
    layout: StorageLayout
    def __init__(self, dataItems: _Optional[_Mapping[str, StorageItem]] = ..., storageOptions: _Optional[_Mapping[str, _type_pb2.Value]] = ..., layout: _Optional[_Union[StorageLayout, str]] = ...) -> None: ...
