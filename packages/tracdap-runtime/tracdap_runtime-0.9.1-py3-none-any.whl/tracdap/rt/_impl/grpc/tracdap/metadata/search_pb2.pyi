from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SEARCH_OPERATOR_NOT_SET: _ClassVar[SearchOperator]
    EQ: _ClassVar[SearchOperator]
    NE: _ClassVar[SearchOperator]
    LT: _ClassVar[SearchOperator]
    LE: _ClassVar[SearchOperator]
    GT: _ClassVar[SearchOperator]
    GE: _ClassVar[SearchOperator]
    IN: _ClassVar[SearchOperator]
    EXISTS: _ClassVar[SearchOperator]

class LogicalOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOGICAL_OPERATOR_NOT_SET: _ClassVar[LogicalOperator]
    AND: _ClassVar[LogicalOperator]
    OR: _ClassVar[LogicalOperator]
    NOT: _ClassVar[LogicalOperator]
SEARCH_OPERATOR_NOT_SET: SearchOperator
EQ: SearchOperator
NE: SearchOperator
LT: SearchOperator
LE: SearchOperator
GT: SearchOperator
GE: SearchOperator
IN: SearchOperator
EXISTS: SearchOperator
LOGICAL_OPERATOR_NOT_SET: LogicalOperator
AND: LogicalOperator
OR: LogicalOperator
NOT: LogicalOperator

class SearchTerm(_message.Message):
    __slots__ = ("attrName", "attrType", "operator", "searchValue")
    ATTRNAME_FIELD_NUMBER: _ClassVar[int]
    ATTRTYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    SEARCHVALUE_FIELD_NUMBER: _ClassVar[int]
    attrName: str
    attrType: _type_pb2.BasicType
    operator: SearchOperator
    searchValue: _type_pb2.Value
    def __init__(self, attrName: _Optional[str] = ..., attrType: _Optional[_Union[_type_pb2.BasicType, str]] = ..., operator: _Optional[_Union[SearchOperator, str]] = ..., searchValue: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...

class LogicalExpression(_message.Message):
    __slots__ = ("operator", "expr")
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    EXPR_FIELD_NUMBER: _ClassVar[int]
    operator: LogicalOperator
    expr: _containers.RepeatedCompositeFieldContainer[SearchExpression]
    def __init__(self, operator: _Optional[_Union[LogicalOperator, str]] = ..., expr: _Optional[_Iterable[_Union[SearchExpression, _Mapping]]] = ...) -> None: ...

class SearchExpression(_message.Message):
    __slots__ = ("term", "logical")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_FIELD_NUMBER: _ClassVar[int]
    term: SearchTerm
    logical: LogicalExpression
    def __init__(self, term: _Optional[_Union[SearchTerm, _Mapping]] = ..., logical: _Optional[_Union[LogicalExpression, _Mapping]] = ...) -> None: ...

class SearchParameters(_message.Message):
    __slots__ = ("objectType", "search", "searchAsOf", "priorVersions", "priorTags")
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    SEARCHASOF_FIELD_NUMBER: _ClassVar[int]
    PRIORVERSIONS_FIELD_NUMBER: _ClassVar[int]
    PRIORTAGS_FIELD_NUMBER: _ClassVar[int]
    objectType: _object_id_pb2.ObjectType
    search: SearchExpression
    searchAsOf: _type_pb2.DatetimeValue
    priorVersions: bool
    priorTags: bool
    def __init__(self, objectType: _Optional[_Union[_object_id_pb2.ObjectType, str]] = ..., search: _Optional[_Union[SearchExpression, _Mapping]] = ..., searchAsOf: _Optional[_Union[_type_pb2.DatetimeValue, _Mapping]] = ..., priorVersions: bool = ..., priorTags: bool = ...) -> None: ...
