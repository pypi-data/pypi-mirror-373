from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import object_id_pb2 as _object_id_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import tag_update_pb2 as _tag_update_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_TYPE_NOT_SET: _ClassVar[JobType]
    RUN_MODEL: _ClassVar[JobType]
    RUN_FLOW: _ClassVar[JobType]
    IMPORT_MODEL: _ClassVar[JobType]
    IMPORT_DATA: _ClassVar[JobType]
    EXPORT_DATA: _ClassVar[JobType]
    JOB_GROUP: _ClassVar[JobType]

class JobStatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_STATUS_CODE_NOT_SET: _ClassVar[JobStatusCode]
    PREPARING: _ClassVar[JobStatusCode]
    VALIDATED: _ClassVar[JobStatusCode]
    PENDING: _ClassVar[JobStatusCode]
    QUEUED: _ClassVar[JobStatusCode]
    SUBMITTED: _ClassVar[JobStatusCode]
    RUNNING: _ClassVar[JobStatusCode]
    FINISHING: _ClassVar[JobStatusCode]
    SUCCEEDED: _ClassVar[JobStatusCode]
    FAILED: _ClassVar[JobStatusCode]
    CANCELLED: _ClassVar[JobStatusCode]

class JobGroupType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JOB_GROUP_TYPE_NOT_SET: _ClassVar[JobGroupType]
    SEQUENTIAL_JOB_GROUP: _ClassVar[JobGroupType]
    PARALLEL_JOB_GROUP: _ClassVar[JobGroupType]
JOB_TYPE_NOT_SET: JobType
RUN_MODEL: JobType
RUN_FLOW: JobType
IMPORT_MODEL: JobType
IMPORT_DATA: JobType
EXPORT_DATA: JobType
JOB_GROUP: JobType
JOB_STATUS_CODE_NOT_SET: JobStatusCode
PREPARING: JobStatusCode
VALIDATED: JobStatusCode
PENDING: JobStatusCode
QUEUED: JobStatusCode
SUBMITTED: JobStatusCode
RUNNING: JobStatusCode
FINISHING: JobStatusCode
SUCCEEDED: JobStatusCode
FAILED: JobStatusCode
CANCELLED: JobStatusCode
JOB_GROUP_TYPE_NOT_SET: JobGroupType
SEQUENTIAL_JOB_GROUP: JobGroupType
PARALLEL_JOB_GROUP: JobGroupType

class JobDefinition(_message.Message):
    __slots__ = ("jobType", "runModel", "runFlow", "importModel", "importData", "exportData", "jobGroup", "resultId")
    JOBTYPE_FIELD_NUMBER: _ClassVar[int]
    RUNMODEL_FIELD_NUMBER: _ClassVar[int]
    RUNFLOW_FIELD_NUMBER: _ClassVar[int]
    IMPORTMODEL_FIELD_NUMBER: _ClassVar[int]
    IMPORTDATA_FIELD_NUMBER: _ClassVar[int]
    EXPORTDATA_FIELD_NUMBER: _ClassVar[int]
    JOBGROUP_FIELD_NUMBER: _ClassVar[int]
    RESULTID_FIELD_NUMBER: _ClassVar[int]
    jobType: JobType
    runModel: RunModelJob
    runFlow: RunFlowJob
    importModel: ImportModelJob
    importData: ImportDataJob
    exportData: ExportDataJob
    jobGroup: JobGroup
    resultId: _object_id_pb2.TagSelector
    def __init__(self, jobType: _Optional[_Union[JobType, str]] = ..., runModel: _Optional[_Union[RunModelJob, _Mapping]] = ..., runFlow: _Optional[_Union[RunFlowJob, _Mapping]] = ..., importModel: _Optional[_Union[ImportModelJob, _Mapping]] = ..., importData: _Optional[_Union[ImportDataJob, _Mapping]] = ..., exportData: _Optional[_Union[ExportDataJob, _Mapping]] = ..., jobGroup: _Optional[_Union[JobGroup, _Mapping]] = ..., resultId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...

class ResultDefinition(_message.Message):
    __slots__ = ("jobId", "statusCode", "statusMessage", "logFileId", "outputs")
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    JOBID_FIELD_NUMBER: _ClassVar[int]
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    STATUSMESSAGE_FIELD_NUMBER: _ClassVar[int]
    LOGFILEID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    jobId: _object_id_pb2.TagSelector
    statusCode: JobStatusCode
    statusMessage: str
    logFileId: _object_id_pb2.TagSelector
    outputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    def __init__(self, jobId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., statusCode: _Optional[_Union[JobStatusCode, str]] = ..., statusMessage: _Optional[str] = ..., logFileId: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., outputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ...) -> None: ...

class RunModelJob(_message.Message):
    __slots__ = ("model", "parameters", "inputs", "outputs", "priorOutputs", "outputAttrs")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class PriorOutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PRIOROUTPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTATTRS_FIELD_NUMBER: _ClassVar[int]
    model: _object_id_pb2.TagSelector
    parameters: _containers.MessageMap[str, _type_pb2.Value]
    inputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    priorOutputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    def __init__(self, model: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., parameters: _Optional[_Mapping[str, _type_pb2.Value]] = ..., inputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., priorOutputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ...) -> None: ...

class RunFlowJob(_message.Message):
    __slots__ = ("flow", "parameters", "inputs", "outputs", "priorOutputs", "models", "outputAttrs")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class PriorOutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class ModelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    FLOW_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PRIOROUTPUTS_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTATTRS_FIELD_NUMBER: _ClassVar[int]
    flow: _object_id_pb2.TagSelector
    parameters: _containers.MessageMap[str, _type_pb2.Value]
    inputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    priorOutputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    models: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    def __init__(self, flow: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., parameters: _Optional[_Mapping[str, _type_pb2.Value]] = ..., inputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., priorOutputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., models: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ...) -> None: ...

class ImportModelJob(_message.Message):
    __slots__ = ("language", "repository", "packageGroup", "package", "version", "entryPoint", "path", "modelAttrs")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    PACKAGEGROUP_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    MODELATTRS_FIELD_NUMBER: _ClassVar[int]
    language: str
    repository: str
    packageGroup: str
    package: str
    version: str
    entryPoint: str
    path: str
    modelAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    def __init__(self, language: _Optional[str] = ..., repository: _Optional[str] = ..., packageGroup: _Optional[str] = ..., package: _Optional[str] = ..., version: _Optional[str] = ..., entryPoint: _Optional[str] = ..., path: _Optional[str] = ..., modelAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ...) -> None: ...

class ImportDataJob(_message.Message):
    __slots__ = ("model", "parameters", "inputs", "outputs", "priorOutputs", "storageAccess", "imports", "outputAttrs", "importAttrs")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class PriorOutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class ImportsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PRIOROUTPUTS_FIELD_NUMBER: _ClassVar[int]
    STORAGEACCESS_FIELD_NUMBER: _ClassVar[int]
    IMPORTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTATTRS_FIELD_NUMBER: _ClassVar[int]
    IMPORTATTRS_FIELD_NUMBER: _ClassVar[int]
    model: _object_id_pb2.TagSelector
    parameters: _containers.MessageMap[str, _type_pb2.Value]
    inputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    priorOutputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    storageAccess: _containers.RepeatedScalarFieldContainer[str]
    imports: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    importAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    def __init__(self, model: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., parameters: _Optional[_Mapping[str, _type_pb2.Value]] = ..., inputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., priorOutputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., storageAccess: _Optional[_Iterable[str]] = ..., imports: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ..., importAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ...) -> None: ...

class ExportDataJob(_message.Message):
    __slots__ = ("model", "parameters", "inputs", "outputs", "priorOutputs", "storageAccess", "exports", "outputAttrs")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class PriorOutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    class ExportsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _object_id_pb2.TagSelector
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ...) -> None: ...
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PRIOROUTPUTS_FIELD_NUMBER: _ClassVar[int]
    STORAGEACCESS_FIELD_NUMBER: _ClassVar[int]
    EXPORTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTATTRS_FIELD_NUMBER: _ClassVar[int]
    model: _object_id_pb2.TagSelector
    parameters: _containers.MessageMap[str, _type_pb2.Value]
    inputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    priorOutputs: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    storageAccess: _containers.RepeatedScalarFieldContainer[str]
    exports: _containers.MessageMap[str, _object_id_pb2.TagSelector]
    outputAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    def __init__(self, model: _Optional[_Union[_object_id_pb2.TagSelector, _Mapping]] = ..., parameters: _Optional[_Mapping[str, _type_pb2.Value]] = ..., inputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., priorOutputs: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., storageAccess: _Optional[_Iterable[str]] = ..., exports: _Optional[_Mapping[str, _object_id_pb2.TagSelector]] = ..., outputAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ...) -> None: ...

class JobGroup(_message.Message):
    __slots__ = ("jobGroupType", "sequential", "parallel")
    JOBGROUPTYPE_FIELD_NUMBER: _ClassVar[int]
    SEQUENTIAL_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_FIELD_NUMBER: _ClassVar[int]
    jobGroupType: JobGroupType
    sequential: SequentialJobGroup
    parallel: ParallelJobGroup
    def __init__(self, jobGroupType: _Optional[_Union[JobGroupType, str]] = ..., sequential: _Optional[_Union[SequentialJobGroup, _Mapping]] = ..., parallel: _Optional[_Union[ParallelJobGroup, _Mapping]] = ...) -> None: ...

class SequentialJobGroup(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobDefinition]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobDefinition, _Mapping]]] = ...) -> None: ...

class ParallelJobGroup(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[JobDefinition]
    def __init__(self, jobs: _Optional[_Iterable[_Union[JobDefinition, _Mapping]]] = ...) -> None: ...
