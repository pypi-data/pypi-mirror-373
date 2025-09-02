from openfl.protocols import base_pb2 as _base_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class TaskResultsRequest(_message.Message):
    __slots__ = ("header", "collab_name", "round_number", "next_step", "execution_environment")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    COLLAB_NAME_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    NEXT_STEP_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    collab_name: str
    round_number: int
    next_step: str
    execution_environment: bytes
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., collab_name: _Optional[str] = ..., round_number: _Optional[int] = ..., next_step: _Optional[str] = ..., execution_environment: _Optional[bytes] = ...) -> None: ...

class TaskResultsResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class GetTasksRequest(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...

class GetTasksResponse(_message.Message):
    __slots__ = ("header", "round_number", "function_name", "execution_environment", "sleep_time", "quit")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    SLEEP_TIME_FIELD_NUMBER: _ClassVar[int]
    QUIT_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    round_number: int
    function_name: str
    execution_environment: bytes
    sleep_time: int
    quit: bool
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., round_number: _Optional[int] = ..., function_name: _Optional[str] = ..., execution_environment: _Optional[bytes] = ..., sleep_time: _Optional[int] = ..., quit: bool = ...) -> None: ...

class CheckpointRequest(_message.Message):
    __slots__ = ("header", "execution_environment", "function", "stream_buffer")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    STREAM_BUFFER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    execution_environment: bytes
    function: bytes
    stream_buffer: bytes
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ..., execution_environment: _Optional[bytes] = ..., function: _Optional[bytes] = ..., stream_buffer: _Optional[bytes] = ...) -> None: ...

class CheckpointResponse(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: MessageHeader
    def __init__(self, header: _Optional[_Union[MessageHeader, _Mapping]] = ...) -> None: ...
