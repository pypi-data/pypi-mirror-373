from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelProto(_message.Message):
    __slots__ = ("tensors",)
    TENSORS_FIELD_NUMBER: _ClassVar[int]
    tensors: _containers.RepeatedCompositeFieldContainer[NamedTensor]
    def __init__(self, tensors: _Optional[_Iterable[_Union[NamedTensor, _Mapping]]] = ...) -> None: ...

class NamedTensor(_message.Message):
    __slots__ = ("name", "round_number", "lossless", "report", "tags", "transformer_metadata", "data_bytes")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    LOSSLESS_FIELD_NUMBER: _ClassVar[int]
    REPORT_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMER_METADATA_FIELD_NUMBER: _ClassVar[int]
    DATA_BYTES_FIELD_NUMBER: _ClassVar[int]
    name: str
    round_number: int
    lossless: bool
    report: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    transformer_metadata: _containers.RepeatedCompositeFieldContainer[MetadataProto]
    data_bytes: bytes
    def __init__(self, name: _Optional[str] = ..., round_number: _Optional[int] = ..., lossless: bool = ..., report: bool = ..., tags: _Optional[_Iterable[str]] = ..., transformer_metadata: _Optional[_Iterable[_Union[MetadataProto, _Mapping]]] = ..., data_bytes: _Optional[bytes] = ...) -> None: ...

class MetadataProto(_message.Message):
    __slots__ = ("int_to_float", "int_list", "bool_list")
    class IntToFloatEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: float
        def __init__(self, key: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...
    INT_TO_FLOAT_FIELD_NUMBER: _ClassVar[int]
    INT_LIST_FIELD_NUMBER: _ClassVar[int]
    BOOL_LIST_FIELD_NUMBER: _ClassVar[int]
    int_to_float: _containers.ScalarMap[int, float]
    int_list: _containers.RepeatedScalarFieldContainer[int]
    bool_list: _containers.RepeatedScalarFieldContainer[bool]
    def __init__(self, int_to_float: _Optional[_Mapping[int, float]] = ..., int_list: _Optional[_Iterable[int]] = ..., bool_list: _Optional[_Iterable[bool]] = ...) -> None: ...

class DataStream(_message.Message):
    __slots__ = ("size", "npbytes")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    NPBYTES_FIELD_NUMBER: _ClassVar[int]
    size: int
    npbytes: bytes
    def __init__(self, size: _Optional[int] = ..., npbytes: _Optional[bytes] = ...) -> None: ...
