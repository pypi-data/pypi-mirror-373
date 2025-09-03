from openfl.protocols import base_pb2 as _base_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageHeader(_message.Message):
    __slots__ = ("sender", "receiver", "federation_uuid", "single_col_cert_common_name")
    SENDER_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_FIELD_NUMBER: _ClassVar[int]
    FEDERATION_UUID_FIELD_NUMBER: _ClassVar[int]
    SINGLE_COL_CERT_COMMON_NAME_FIELD_NUMBER: _ClassVar[int]
    sender: str
    receiver: str
    federation_uuid: str
    single_col_cert_common_name: str
    def __init__(self, sender: _Optional[str] = ..., receiver: _Optional[str] = ..., federation_uuid: _Optional[str] = ..., single_col_cert_common_name: _Optional[str] = ...) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class GetTasksRequest(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("name", "function_name", "task_type", "apply_local")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    APPLY_LOCAL_FIELD_NUMBER: _ClassVar[int]
    name: str
    function_name: str
    task_type: str
    apply_local: bool
    def __init__(self, name: _Optional[str] = ..., function_name: _Optional[str] = ..., task_type: _Optional[str] = ..., apply_local: bool = ...) -> None: ...

class GetTasksResponse(_message.Message):
    __slots__ = ("header", "round_number", "tasks", "sleep_time", "quit")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    SLEEP_TIME_FIELD_NUMBER: _ClassVar[int]
    QUIT_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    round_number: int
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    sleep_time: int
    quit: bool
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., round_number: _Optional[int] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., sleep_time: _Optional[int] = ..., quit: bool = ...) -> None: ...

class GetAggregatedTensorRequest(_message.Message):
    __slots__ = ("header", "tensor_name", "round_number", "report", "tags", "require_lossless")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    TENSOR_NAME_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_LOSSLESS_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    tensor_name: str
    round_number: int
    report: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    require_lossless: bool
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., tensor_name: _Optional[str] = ..., round_number: _Optional[int] = ..., report: bool = ..., tags: _Optional[_Iterable[str]] = ..., require_lossless: bool = ...) -> None: ...

class GetAggregatedTensorResponse(_message.Message):
    __slots__ = ("header", "round_number", "tensor")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TENSOR_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    round_number: int
    tensor: _base_pb2.NamedTensor
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., round_number: _Optional[int] = ..., tensor: _Optional[_Union[_base_pb2.NamedTensor, _Mapping]] = ...) -> None: ...

class TaskResults(_message.Message):
    __slots__ = ("header", "round_number", "task_name", "data_size", "tensors")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_SIZE_FIELD_NUMBER: _ClassVar[int]
    TENSORS_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    round_number: int
    task_name: str
    data_size: int
    tensors: _containers.RepeatedCompositeFieldContainer[_base_pb2.NamedTensor]
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., round_number: _Optional[int] = ..., task_name: _Optional[str] = ..., data_size: _Optional[int] = ..., tensors: _Optional[_Iterable[_Union[_base_pb2.NamedTensor, _Mapping]]] = ...) -> None: ...

class SendLocalTaskResultsResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class InteropMessage(_message.Message):
    __slots__ = ("header", "message", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HEADER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    message: _base_pb2.DataStream
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., message: _Optional[_Union[_base_pb2.DataStream, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...
