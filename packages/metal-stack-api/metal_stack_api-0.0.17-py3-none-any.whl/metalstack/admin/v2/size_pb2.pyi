from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import size_pb2 as _size_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SizeServiceCreateRequest(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _size_pb2.Size
    def __init__(self, size: _Optional[_Union[_size_pb2.Size, _Mapping]] = ...) -> None: ...

class SizeServiceCreateResponse(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _size_pb2.Size
    def __init__(self, size: _Optional[_Union[_size_pb2.Size, _Mapping]] = ...) -> None: ...

class SizeServiceUpdateRequest(_message.Message):
    __slots__ = ("id", "name", "description", "constraints", "labels")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    constraints: _containers.RepeatedCompositeFieldContainer[_size_pb2.SizeConstraint]
    labels: _common_pb2.UpdateLabels
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., constraints: _Optional[_Iterable[_Union[_size_pb2.SizeConstraint, _Mapping]]] = ..., labels: _Optional[_Union[_common_pb2.UpdateLabels, _Mapping]] = ...) -> None: ...

class SizeServiceUpdateResponse(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _size_pb2.Size
    def __init__(self, size: _Optional[_Union[_size_pb2.Size, _Mapping]] = ...) -> None: ...

class SizeServiceDeleteRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SizeServiceDeleteResponse(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: _size_pb2.Size
    def __init__(self, size: _Optional[_Union[_size_pb2.Size, _Mapping]] = ...) -> None: ...
