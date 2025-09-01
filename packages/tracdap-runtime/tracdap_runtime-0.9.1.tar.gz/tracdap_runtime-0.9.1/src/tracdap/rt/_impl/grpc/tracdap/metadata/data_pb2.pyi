from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SchemaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SCHEMA_TYPE_NOT_SET: _ClassVar[SchemaType]
    TABLE_SCHEMA: _ClassVar[SchemaType]
    TABLE: _ClassVar[SchemaType]
    STRUCT_SCHEMA: _ClassVar[SchemaType]

class PartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PART_ROOT: _ClassVar[PartType]
    NOT_PARTITIONED: _ClassVar[PartType]
    PART_BY_RANGE: _ClassVar[PartType]
    PART_BY_VALUE: _ClassVar[PartType]
SCHEMA_TYPE_NOT_SET: SchemaType
TABLE_SCHEMA: SchemaType
TABLE: SchemaType
STRUCT_SCHEMA: SchemaType
PART_ROOT: PartType
NOT_PARTITIONED: PartType
PART_BY_RANGE: PartType
PART_BY_VALUE: PartType

class FieldSchema(_message.Message):
    __slots__ = ("fieldName", "fieldOrder", "fieldType", "label", "businessKey", "categorical", "notNull", "formatCode", "defaultValue", "namedType", "namedEnum", "children")
    FIELDNAME_FIELD_NUMBER: _ClassVar[int]
    FIELDORDER_FIELD_NUMBER: _ClassVar[int]
    FIELDTYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    BUSINESSKEY_FIELD_NUMBER: _ClassVar[int]
    CATEGORICAL_FIELD_NUMBER: _ClassVar[int]
    NOTNULL_FIELD_NUMBER: _ClassVar[int]
    FORMATCODE_FIELD_NUMBER: _ClassVar[int]
    DEFAULTVALUE_FIELD_NUMBER: _ClassVar[int]
    NAMEDTYPE_FIELD_NUMBER: _ClassVar[int]
    NAMEDENUM_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    fieldName: str
    fieldOrder: int
    fieldType: _type_pb2.BasicType
    label: str
    businessKey: bool
    categorical: bool
    notNull: bool
    formatCode: str
    defaultValue: _type_pb2.Value
    namedType: str
    namedEnum: str
    children: _containers.RepeatedCompositeFieldContainer[FieldSchema]
    def __init__(self, fieldName: _Optional[str] = ..., fieldOrder: _Optional[int] = ..., fieldType: _Optional[_Union[_type_pb2.BasicType, str]] = ..., label: _Optional[str] = ..., businessKey: bool = ..., categorical: bool = ..., notNull: bool = ..., formatCode: _Optional[str] = ..., defaultValue: _Optional[_Union[_type_pb2.Value, _Mapping]] = ..., namedType: _Optional[str] = ..., namedEnum: _Optional[str] = ..., children: _Optional[_Iterable[_Union[FieldSchema, _Mapping]]] = ...) -> None: ...

class EnumValues(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class TableSchema(_message.Message):
    __slots__ = ("fields",)
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedCompositeFieldContainer[FieldSchema]
    def __init__(self, fields: _Optional[_Iterable[_Union[FieldSchema, _Mapping]]] = ...) -> None: ...

class StructSchema(_message.Message):
    __slots__ = ("fields",)
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.RepeatedCompositeFieldContainer[FieldSchema]
    def __init__(self, fields: _Optional[_Iterable[_Union[FieldSchema, _Mapping]]] = ...) -> None: ...

class SchemaDefinition(_message.Message):
    __slots__ = ("schemaType", "partType", "table", "struct", "namedTypes", "namedEnums")
    class NamedTypesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SchemaDefinition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SchemaDefinition, _Mapping]] = ...) -> None: ...
    class NamedEnumsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: EnumValues
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[EnumValues, _Mapping]] = ...) -> None: ...
    SCHEMATYPE_FIELD_NUMBER: _ClassVar[int]
    PARTTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    STRUCT_FIELD_NUMBER: _ClassVar[int]
    NAMEDTYPES_FIELD_NUMBER: _ClassVar[int]
    NAMEDENUMS_FIELD_NUMBER: _ClassVar[int]
    schemaType: SchemaType
    partType: PartType
    table: TableSchema
    struct: StructSchema
    namedTypes: _containers.MessageMap[str, SchemaDefinition]
    namedEnums: _containers.MessageMap[str, EnumValues]
    def __init__(self, schemaType: _Optional[_Union[SchemaType, str]] = ..., partType: _Optional[_Union[PartType, str]] = ..., table: _Optional[_Union[TableSchema, _Mapping]] = ..., struct: _Optional[_Union[StructSchema, _Mapping]] = ..., namedTypes: _Optional[_Mapping[str, SchemaDefinition]] = ..., namedEnums: _Optional[_Mapping[str, EnumValues]] = ...) -> None: ...

class PartKey(_message.Message):
    __slots__ = ("opaqueKey", "partType", "partValues", "partRangeMin", "partRangeMax")
    OPAQUEKEY_FIELD_NUMBER: _ClassVar[int]
    PARTTYPE_FIELD_NUMBER: _ClassVar[int]
    PARTVALUES_FIELD_NUMBER: _ClassVar[int]
    PARTRANGEMIN_FIELD_NUMBER: _ClassVar[int]
    PARTRANGEMAX_FIELD_NUMBER: _ClassVar[int]
    opaqueKey: str
    partType: PartType
    partValues: _containers.RepeatedCompositeFieldContainer[_type_pb2.Value]
    partRangeMin: _type_pb2.Value
    partRangeMax: _type_pb2.Value
    def __init__(self, opaqueKey: _Optional[str] = ..., partType: _Optional[_Union[PartType, str]] = ..., partValues: _Optional[_Iterable[_Union[_type_pb2.Value, _Mapping]]] = ..., partRangeMin: _Optional[_Union[_type_pb2.Value, _Mapping]] = ..., partRangeMax: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...

class DataDelta(_message.Message):
    __slots__ = ("deltaIndex", "dataItem", "physicalRowCount", "deltaRowCount")
    DELTAINDEX_FIELD_NUMBER: _ClassVar[int]
    DATAITEM_FIELD_NUMBER: _ClassVar[int]
    PHYSICALROWCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELTAROWCOUNT_FIELD_NUMBER: _ClassVar[int]
    deltaIndex: int
    dataItem: str
    physicalRowCount: int
    deltaRowCount: int
    def __init__(self, deltaIndex: _Optional[int] = ..., dataItem: _Optional[str] = ..., physicalRowCount: _Optional[int] = ..., deltaRowCount: _Optional[int] = ...) -> None: ...

class DataSnapshot(_message.Message):
    __slots__ = ("snapIndex", "deltas")
    SNAPINDEX_FIELD_NUMBER: _ClassVar[int]
    DELTAS_FIELD_NUMBER: _ClassVar[int]
    snapIndex: int
    deltas: _containers.RepeatedCompositeFieldContainer[DataDelta]
    def __init__(self, snapIndex: _Optional[int] = ..., deltas: _Optional[_Iterable[_Union[DataDelta, _Mapping]]] = ...) -> None: ...

class DataPartition(_message.Message):
    __slots__ = ("partKey", "snap")
    PARTKEY_FIELD_NUMBER: _ClassVar[int]
    SNAP_FIELD_NUMBER: _ClassVar[int]
    partKey: PartKey
    snap: DataSnapshot
    def __init__(self, partKey: _Optional[_Union[PartKey, _Mapping]] = ..., snap: _Optional[_Union[DataSnapshot, _Mapping]] = ...) -> None: ...

class DataDefinition(_message.Message):
    __slots__ = ("schemaId", "schema", "parts", "storageId", "rowCount")
    class PartsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: DataPartition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[DataPartition, _Mapping]] = ...) -> None: ...
    SCHEMAID_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    PARTS_FIELD_NUMBER: _ClassVar[int]
    STORAGEID_FIELD_NUMBER: _ClassVar[int]
    ROWCOUNT_FIELD_NUMBER: _ClassVar[int]
    schemaId: _object_id_pb2.TagSelector
    schema: SchemaDefinition
    parts: _containers.MessageMap[str, DataPartition]
    storageId: _object_id_pb2.TagSelector
    rowCount: int
    def __init__(self, schemaId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., schema: _Optional[_Union[SchemaDefinition, _Mapping]] = ..., parts: _Optional[_Mapping[str, DataPartition]] = ..., storageId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., rowCount: _Optional[int] = ...) -> None: ...
