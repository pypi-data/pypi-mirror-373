from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileDefinition(_message.Message):
    __slots__ = ("name", "extension", "mimeType", "size", "storageId", "dataItem")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    STORAGEID_FIELD_NUMBER: _ClassVar[int]
    DATAITEM_FIELD_NUMBER: _ClassVar[int]
    name: str
    extension: str
    mimeType: str
    size: int
    storageId: _object_id_pb2.TagSelector
    dataItem: str
    def __init__(self, name: _Optional[str] = ..., extension: _Optional[str] = ..., mimeType: _Optional[str] = ..., size: _Optional[int] = ..., storageId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., dataItem: _Optional[str] = ...) -> None: ...

class FileType(_message.Message):
    __slots__ = ("extension", "mimeType")
    EXTENSION_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    extension: str
    mimeType: str
    def __init__(self, extension: _Optional[str] = ..., mimeType: _Optional[str] = ...) -> None: ...
