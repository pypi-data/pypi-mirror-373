from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TagOperation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CREATE_OR_REPLACE_ATTR: _ClassVar[TagOperation]
    CREATE_OR_APPEND_ATTR: _ClassVar[TagOperation]
    CREATE_ATTR: _ClassVar[TagOperation]
    REPLACE_ATTR: _ClassVar[TagOperation]
    APPEND_ATTR: _ClassVar[TagOperation]
    DELETE_ATTR: _ClassVar[TagOperation]
    CLEAR_ALL_ATTR: _ClassVar[TagOperation]
CREATE_OR_REPLACE_ATTR: TagOperation
CREATE_OR_APPEND_ATTR: TagOperation
CREATE_ATTR: TagOperation
REPLACE_ATTR: TagOperation
APPEND_ATTR: TagOperation
DELETE_ATTR: TagOperation
CLEAR_ALL_ATTR: TagOperation

class TagUpdate(_message.Message):
    __slots__ = ("operation", "attrName", "value")
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    ATTRNAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    operation: TagOperation
    attrName: str
    value: _type_pb2.Value
    def __init__(self, operation: _Optional[_Union[TagOperation, str]] = ..., attrName: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
