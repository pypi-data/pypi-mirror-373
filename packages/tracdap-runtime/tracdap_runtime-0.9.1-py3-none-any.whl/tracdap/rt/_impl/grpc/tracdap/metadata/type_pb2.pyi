from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BasicType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BASIC_TYPE_NOT_SET: _ClassVar[BasicType]
    BOOLEAN: _ClassVar[BasicType]
    INTEGER: _ClassVar[BasicType]
    FLOAT: _ClassVar[BasicType]
    STRING: _ClassVar[BasicType]
    DECIMAL: _ClassVar[BasicType]
    DATE: _ClassVar[BasicType]
    DATETIME: _ClassVar[BasicType]
    ARRAY: _ClassVar[BasicType]
    MAP: _ClassVar[BasicType]
    STRUCT: _ClassVar[BasicType]
BASIC_TYPE_NOT_SET: BasicType
BOOLEAN: BasicType
INTEGER: BasicType
FLOAT: BasicType
STRING: BasicType
DECIMAL: BasicType
DATE: BasicType
DATETIME: BasicType
ARRAY: BasicType
MAP: BasicType
STRUCT: BasicType

class TypeDescriptor(_message.Message):
    __slots__ = ("basicType", "arrayType", "mapType", "structTypes", "typeName")
    class StructTypesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TypeDescriptor
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TypeDescriptor, _Mapping]] = ...) -> None: ...
    BASICTYPE_FIELD_NUMBER: _ClassVar[int]
    ARRAYTYPE_FIELD_NUMBER: _ClassVar[int]
    MAPTYPE_FIELD_NUMBER: _ClassVar[int]
    STRUCTTYPES_FIELD_NUMBER: _ClassVar[int]
    TYPENAME_FIELD_NUMBER: _ClassVar[int]
    basicType: BasicType
    arrayType: TypeDescriptor
    mapType: TypeDescriptor
    structTypes: _containers.MessageMap[str, TypeDescriptor]
    typeName: str
    def __init__(self, basicType: _Optional[_Union[BasicType, str]] = ..., arrayType: _Optional[_Union[TypeDescriptor, _Mapping]] = ..., mapType: _Optional[_Union[TypeDescriptor, _Mapping]] = ..., structTypes: _Optional[_Mapping[str, TypeDescriptor]] = ..., typeName: _Optional[str] = ...) -> None: ...

class DecimalValue(_message.Message):
    __slots__ = ("decimal",)
    DECIMAL_FIELD_NUMBER: _ClassVar[int]
    decimal: str
    def __init__(self, decimal: _Optional[str] = ...) -> None: ...

class DateValue(_message.Message):
    __slots__ = ("isoDate",)
    ISODATE_FIELD_NUMBER: _ClassVar[int]
    isoDate: str
    def __init__(self, isoDate: _Optional[str] = ...) -> None: ...

class DatetimeValue(_message.Message):
    __slots__ = ("isoDatetime",)
    ISODATETIME_FIELD_NUMBER: _ClassVar[int]
    isoDatetime: str
    def __init__(self, isoDatetime: _Optional[str] = ...) -> None: ...

class Value(_message.Message):
    __slots__ = ("type", "booleanValue", "integerValue", "floatValue", "stringValue", "decimalValue", "dateValue", "datetimeValue", "arrayValue", "mapValue")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BOOLEANVALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGERVALUE_FIELD_NUMBER: _ClassVar[int]
    FLOATVALUE_FIELD_NUMBER: _ClassVar[int]
    STRINGVALUE_FIELD_NUMBER: _ClassVar[int]
    DECIMALVALUE_FIELD_NUMBER: _ClassVar[int]
    DATEVALUE_FIELD_NUMBER: _ClassVar[int]
    DATETIMEVALUE_FIELD_NUMBER: _ClassVar[int]
    ARRAYVALUE_FIELD_NUMBER: _ClassVar[int]
    MAPVALUE_FIELD_NUMBER: _ClassVar[int]
    type: TypeDescriptor
    booleanValue: bool
    integerValue: int
    floatValue: float
    stringValue: str
    decimalValue: DecimalValue
    dateValue: DateValue
    datetimeValue: DatetimeValue
    arrayValue: ArrayValue
    mapValue: MapValue
    def __init__(self, type: _Optional[_Union[TypeDescriptor, _Mapping]] = ..., booleanValue: bool = ..., integerValue: _Optional[int] = ..., floatValue: _Optional[float] = ..., stringValue: _Optional[str] = ..., decimalValue: _Optional[_Union[DecimalValue, _Mapping]] = ..., dateValue: _Optional[_Union[DateValue, _Mapping]] = ..., datetimeValue: _Optional[_Union[DatetimeValue, _Mapping]] = ..., arrayValue: _Optional[_Union[ArrayValue, _Mapping]] = ..., mapValue: _Optional[_Union[MapValue, _Mapping]] = ...) -> None: ...

class ArrayValue(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[Value]
    def __init__(self, items: _Optional[_Iterable[_Union[Value, _Mapping]]] = ...) -> None: ...

class MapValue(_message.Message):
    __slots__ = ("entries",)
    class EntriesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Value, _Mapping]] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.MessageMap[str, Value]
    def __init__(self, entries: _Optional[_Mapping[str, Value]] = ...) -> None: ...
