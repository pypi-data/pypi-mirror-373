from tracdap.rt._impl.grpc.tracdap.metadata import type_pb2 as _type_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import model_pb2 as _model_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import search_pb2 as _search_pb2
from tracdap.rt._impl.grpc.tracdap.metadata import tag_update_pb2 as _tag_update_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FlowNodeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_TYPE_NOT_SET: _ClassVar[FlowNodeType]
    INPUT_NODE: _ClassVar[FlowNodeType]
    OUTPUT_NODE: _ClassVar[FlowNodeType]
    MODEL_NODE: _ClassVar[FlowNodeType]
    PARAMETER_NODE: _ClassVar[FlowNodeType]
NODE_TYPE_NOT_SET: FlowNodeType
INPUT_NODE: FlowNodeType
OUTPUT_NODE: FlowNodeType
MODEL_NODE: FlowNodeType
PARAMETER_NODE: FlowNodeType

class FlowNode(_message.Message):
    __slots__ = ("nodeType", "parameters", "inputs", "outputs", "nodeSearch", "nodeAttrs", "nodeProps", "label")
    class NodePropsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _type_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_type_pb2.Value, _Mapping]] = ...) -> None: ...
    NODETYPE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    NODESEARCH_FIELD_NUMBER: _ClassVar[int]
    NODEATTRS_FIELD_NUMBER: _ClassVar[int]
    NODEPROPS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    nodeType: FlowNodeType
    parameters: _containers.RepeatedScalarFieldContainer[str]
    inputs: _containers.RepeatedScalarFieldContainer[str]
    outputs: _containers.RepeatedScalarFieldContainer[str]
    nodeSearch: _search_pb2.SearchExpression
    nodeAttrs: _containers.RepeatedCompositeFieldContainer[_tag_update_pb2.TagUpdate]
    nodeProps: _containers.MessageMap[str, _type_pb2.Value]
    label: str
    def __init__(self, nodeType: _Optional[_Union[FlowNodeType, str]] = ..., parameters: _Optional[_Iterable[str]] = ..., inputs: _Optional[_Iterable[str]] = ..., outputs: _Optional[_Iterable[str]] = ..., nodeSearch: _Optional[_Union[_search_pb2.SearchExpression, _Mapping]] = ..., nodeAttrs: _Optional[_Iterable[_Union[_tag_update_pb2.TagUpdate, _Mapping]]] = ..., nodeProps: _Optional[_Mapping[str, _type_pb2.Value]] = ..., label: _Optional[str] = ...) -> None: ...

class FlowSocket(_message.Message):
    __slots__ = ("node", "socket")
    NODE_FIELD_NUMBER: _ClassVar[int]
    SOCKET_FIELD_NUMBER: _ClassVar[int]
    node: str
    socket: str
    def __init__(self, node: _Optional[str] = ..., socket: _Optional[str] = ...) -> None: ...

class FlowEdge(_message.Message):
    __slots__ = ("source", "target")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    source: FlowSocket
    target: FlowSocket
    def __init__(self, source: _Optional[_Union[FlowSocket, _Mapping]] = ..., target: _Optional[_Union[FlowSocket, _Mapping]] = ...) -> None: ...

class FlowDefinition(_message.Message):
    __slots__ = ("nodes", "edges", "parameters", "inputs", "outputs")
    class NodesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FlowNode
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FlowNode, _Mapping]] = ...) -> None: ...
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _model_pb2.ModelParameter
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_model_pb2.ModelParameter, _Mapping]] = ...) -> None: ...
    class InputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _model_pb2.ModelInputSchema
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_model_pb2.ModelInputSchema, _Mapping]] = ...) -> None: ...
    class OutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _model_pb2.ModelOutputSchema
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_model_pb2.ModelOutputSchema, _Mapping]] = ...) -> None: ...
    NODES_FIELD_NUMBER: _ClassVar[int]
    EDGES_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.MessageMap[str, FlowNode]
    edges: _containers.RepeatedCompositeFieldContainer[FlowEdge]
    parameters: _containers.MessageMap[str, _model_pb2.ModelParameter]
    inputs: _containers.MessageMap[str, _model_pb2.ModelInputSchema]
    outputs: _containers.MessageMap[str, _model_pb2.ModelOutputSchema]
    def __init__(self, nodes: _Optional[_Mapping[str, FlowNode]] = ..., edges: _Optional[_Iterable[_Union[FlowEdge, _Mapping]]] = ..., parameters: _Optional[_Mapping[str, _model_pb2.ModelParameter]] = ..., inputs: _Optional[_Mapping[str, _model_pb2.ModelInputSchema]] = ..., outputs: _Optional[_Mapping[str, _model_pb2.ModelOutputSchema]] = ...) -> None: ...
