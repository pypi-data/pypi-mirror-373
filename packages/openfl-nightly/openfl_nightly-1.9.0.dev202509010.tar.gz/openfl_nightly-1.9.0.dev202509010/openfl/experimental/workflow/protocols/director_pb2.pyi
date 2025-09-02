from openfl.protocols import base_pb2 as _base_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SendConnectionRequest(_message.Message):
    __slots__ = ("envoy_name",)
    ENVOY_NAME_FIELD_NUMBER: _ClassVar[int]
    envoy_name: str
    def __init__(self, envoy_name: _Optional[str] = ...) -> None: ...

class RequestAccepted(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class WaitExperimentRequest(_message.Message):
    __slots__ = ("collaborator_name",)
    COLLABORATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    collaborator_name: str
    def __init__(self, collaborator_name: _Optional[str] = ...) -> None: ...

class WaitExperimentResponse(_message.Message):
    __slots__ = ("experiment_name",)
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    experiment_name: str
    def __init__(self, experiment_name: _Optional[str] = ...) -> None: ...

class GetExperimentDataRequest(_message.Message):
    __slots__ = ("experiment_name", "collaborator_name")
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    COLLABORATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    experiment_name: str
    collaborator_name: str
    def __init__(self, experiment_name: _Optional[str] = ..., collaborator_name: _Optional[str] = ...) -> None: ...

class ExperimentData(_message.Message):
    __slots__ = ("size", "exp_data")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    EXP_DATA_FIELD_NUMBER: _ClassVar[int]
    size: int
    exp_data: bytes
    def __init__(self, size: _Optional[int] = ..., exp_data: _Optional[bytes] = ...) -> None: ...

class UpdateEnvoyStatusRequest(_message.Message):
    __slots__ = ("name", "is_experiment_running")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_EXPERIMENT_RUNNING_FIELD_NUMBER: _ClassVar[int]
    name: str
    is_experiment_running: bool
    def __init__(self, name: _Optional[str] = ..., is_experiment_running: bool = ...) -> None: ...

class UpdateEnvoyStatusResponse(_message.Message):
    __slots__ = ("health_check_period",)
    HEALTH_CHECK_PERIOD_FIELD_NUMBER: _ClassVar[int]
    health_check_period: _duration_pb2.Duration
    def __init__(self, health_check_period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ExperimentInfo(_message.Message):
    __slots__ = ("name", "collaborator_names", "experiment_data")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLLABORATOR_NAMES_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_DATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    collaborator_names: _containers.RepeatedScalarFieldContainer[str]
    experiment_data: ExperimentData
    def __init__(self, name: _Optional[str] = ..., collaborator_names: _Optional[_Iterable[str]] = ..., experiment_data: _Optional[_Union[ExperimentData, _Mapping]] = ...) -> None: ...

class SetNewExperimentResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class EnvoyInfo(_message.Message):
    __slots__ = ("envoy_name", "experiment_name", "is_online", "is_experiment_running", "last_updated", "valid_duration")
    ENVOY_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ONLINE_FIELD_NUMBER: _ClassVar[int]
    IS_EXPERIMENT_RUNNING_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    VALID_DURATION_FIELD_NUMBER: _ClassVar[int]
    envoy_name: str
    experiment_name: str
    is_online: bool
    is_experiment_running: bool
    last_updated: _timestamp_pb2.Timestamp
    valid_duration: _duration_pb2.Duration
    def __init__(self, envoy_name: _Optional[str] = ..., experiment_name: _Optional[str] = ..., is_online: bool = ..., is_experiment_running: bool = ..., last_updated: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., valid_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class GetEnvoysRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetEnvoysResponse(_message.Message):
    __slots__ = ("envoy_infos",)
    ENVOY_INFOS_FIELD_NUMBER: _ClassVar[int]
    envoy_infos: _containers.RepeatedCompositeFieldContainer[EnvoyInfo]
    def __init__(self, envoy_infos: _Optional[_Iterable[_Union[EnvoyInfo, _Mapping]]] = ...) -> None: ...

class GetFlowStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetFlowStateResponse(_message.Message):
    __slots__ = ("completed", "flspec_obj")
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    FLSPEC_OBJ_FIELD_NUMBER: _ClassVar[int]
    completed: bool
    flspec_obj: bytes
    def __init__(self, completed: bool = ..., flspec_obj: _Optional[bytes] = ...) -> None: ...

class SendRuntimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RuntimeRequestResponse(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class GetExperimentStdoutRequest(_message.Message):
    __slots__ = ("experiment_name",)
    EXPERIMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    experiment_name: str
    def __init__(self, experiment_name: _Optional[str] = ...) -> None: ...

class GetExperimentStdoutResponse(_message.Message):
    __slots__ = ("stdout_origin", "task_name", "stdout_value")
    STDOUT_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    STDOUT_VALUE_FIELD_NUMBER: _ClassVar[int]
    stdout_origin: str
    task_name: str
    stdout_value: str
    def __init__(self, stdout_origin: _Optional[str] = ..., task_name: _Optional[str] = ..., stdout_value: _Optional[str] = ...) -> None: ...
