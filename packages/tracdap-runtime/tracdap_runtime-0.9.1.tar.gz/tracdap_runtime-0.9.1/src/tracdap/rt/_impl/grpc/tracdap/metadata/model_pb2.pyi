from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import data_pb2 as _data_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import file_pb2 as _file_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STANDARD_MODEL: _ClassVar[ModelType]
    DATA_IMPORT_MODEL: _ClassVar[ModelType]
    DATA_EXPORT_MODEL: _ClassVar[ModelType]
STANDARD_MODEL: ModelType
DATA_IMPORT_MODEL: ModelType
DATA_EXPORT_MODEL: ModelType

class ModelParameter(_message.Message):
    __slots__ = ("paramType", "label", "defaultValue", "paramProps")
    class ParamPropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    PARAMTYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DEFAULTVALUE_FIELD_NUMBER: _ClassVar[int]
    PARAMPROPS_FIELD_NUMBER: _ClassVar[int]
    paramType: _type_pb2.TypeDescriptor
    label: str
    defaultValue: _type_pb2.Value
    paramProps: _containers.MessageMap[str, _type_pb2.Value]
    def __init__(self, paramType: _Optional[_Union[_type_pb2.TypeDescriptor, _Mapping]] = ..., label: _Optional[str] = ..., defaultValue: _Optional[_Union[_type_pb2.Value, _Mapping]] = ..., paramProps: _Optional[_Mapping[str, _type_pb2.Value]] = ...) -> None: ...

class ModelInputSchema(_message.Message):
    __slots__ = ("objectType", "schema", "fileType", "label", "optional", "dynamic", "inputProps")
    class InputPropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FILETYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_FIELD_NUMBER: _ClassVar[int]
    INPUTPROPS_FIELD_NUMBER: _ClassVar[int]
    objectType: _object_id_pb2.ObjectType
    schema: _data_pb2.SchemaDefinition
    fileType: _file_pb2.FileType
    label: str
    optional: bool
    dynamic: bool
    inputProps: _containers.MessageMap[str, _type_pb2.Value]
    def __init__(self, objectType: _Optional[_Union[_object_id_pb2.ObjectType, str]] = ..., schema: _Optional[_Union[_data_pb2.SchemaDefinition, _Mapping]] = ..., fileType: _Optional[_Union[_file_pb2.FileType, _Mapping]] = ..., label: _Optional[str] = ..., optional: bool = ..., dynamic: bool = ..., inputProps: _Optional[_Mapping[str, _type_pb2.Value]] = ...) -> None: ...

class ModelOutputSchema(_message.Message):
    __slots__ = ("objectType", "schema", "fileType", "label", "optional", "dynamic", "outputProps")
    class OutputPropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    OBJECTTYPE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FILETYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_FIELD_NUMBER: _ClassVar[int]
    OUTPUTPROPS_FIELD_NUMBER: _ClassVar[int]
    objectType: _object_id_pb2.ObjectType
    schema: _data_pb2.SchemaDefinition
    fileType: _file_pb2.FileType
    label: str
    optional: bool
    dynamic: bool
    outputProps: _containers.MessageMap[str, _type_pb2.Value]
    def __init__(self, objectType: _Optional[_Union[_object_id_pb2.ObjectType, str]] = ..., schema: _Optional[_Union[_data_pb2.SchemaDefinition, _Mapping]] = ..., fileType: _Optional[_Union[_file_pb2.FileType, _Mapping]] = ..., label: _Optional[str] = ..., optional: bool = ..., dynamic: bool = ..., outputProps: _Optional[_Mapping[str, _type_pb2.Value]] = ...) -> None: ...

class ModelDefinition(_message.Message):
    __slots__ = ("language", "repository", "packageGroup", "package", "version", "entryPoint", "path", "parameters", "inputs", "outputs", "staticAttributes", "modelType")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ModelParameter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ModelParameter, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ModelInputSchema
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ModelInputSchema, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ModelOutputSchema
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ModelOutputSchema, _Mapping]] = ...) -> None: ...
    class StaticAttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    PACKAGEGROUP_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    STATICATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    MODELTYPE_FIELD_NUMBER: _ClassVar[int]
    language: str
    repository: str
    packageGroup: str
    package: str
    version: str
    entryPoint: str
    path: str
    parameters: _containers.MessageMap[str, ModelParameter]
    inputs: _containers.MessageMap[str, ModelInputSchema]
    outputs: _containers.MessageMap[str, ModelOutputSchema]
    staticAttributes: _containers.MessageMap[str, _type_pb2.Value]
    modelType: ModelType
    def __init__(self, language: _Optional[str] = ..., repository: _Optional[str] = ..., packageGroup: _Optional[str] = ..., package: _Optional[str] = ..., version: _Optional[str] = ..., entryPoint: _Optional[str] = ..., path: _Optional[str] = ..., parameters: _Optional[_Mapping[str, ModelParameter]] = ..., inputs: _Optional[_Mapping[str, ModelInputSchema]] = ..., outputs: _Optional[_Mapping[str, ModelOutputSchema]] = ..., staticAttributes: _Optional[_Mapping[str, _type_pb2.Value]] = ..., modelType: _Optional[_Union[ModelType, str]] = ...) -> None: ...
