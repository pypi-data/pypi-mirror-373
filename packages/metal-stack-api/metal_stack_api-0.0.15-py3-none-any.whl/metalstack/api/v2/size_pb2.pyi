from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SizeConstraintType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIZE_CONSTRAINT_TYPE_UNSPECIFIED: _ClassVar[SizeConstraintType]
    SIZE_CONSTRAINT_TYPE_CORES: _ClassVar[SizeConstraintType]
    SIZE_CONSTRAINT_TYPE_MEMORY: _ClassVar[SizeConstraintType]
    SIZE_CONSTRAINT_TYPE_STORAGE: _ClassVar[SizeConstraintType]
    SIZE_CONSTRAINT_TYPE_GPU: _ClassVar[SizeConstraintType]
SIZE_CONSTRAINT_TYPE_UNSPECIFIED: SizeConstraintType
SIZE_CONSTRAINT_TYPE_CORES: SizeConstraintType
SIZE_CONSTRAINT_TYPE_MEMORY: SizeConstraintType
SIZE_CONSTRAINT_TYPE_STORAGE: SizeConstraintType
SIZE_CONSTRAINT_TYPE_GPU: SizeConstraintType

class SizeServiceGetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class SizeServiceListRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: SizeQuery
    def __init__(self, query: _Optional[_Union[SizeQuery, _Mapping]] = ...) -> None: ...

class SizeServiceGetResponse(_message.Message):
    __slots__ = ("size",)
    SIZE_FIELD_NUMBER: _ClassVar[int]
    size: Size
    def __init__(self, size: _Optional[_Union[Size, _Mapping]] = ...) -> None: ...

class SizeServiceListResponse(_message.Message):
    __slots__ = ("sizes",)
    SIZES_FIELD_NUMBER: _ClassVar[int]
    sizes: _containers.RepeatedCompositeFieldContainer[Size]
    def __init__(self, sizes: _Optional[_Iterable[_Union[Size, _Mapping]]] = ...) -> None: ...

class Size(_message.Message):
    __slots__ = ("id", "meta", "name", "description", "constraints")
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    meta: _common_pb2.Meta
    name: str
    description: str
    constraints: _containers.RepeatedCompositeFieldContainer[SizeConstraint]
    def __init__(self, id: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., constraints: _Optional[_Iterable[_Union[SizeConstraint, _Mapping]]] = ...) -> None: ...

class SizeConstraint(_message.Message):
    __slots__ = ("type", "min", "max", "identifier")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    type: SizeConstraintType
    min: int
    max: int
    identifier: str
    def __init__(self, type: _Optional[_Union[SizeConstraintType, str]] = ..., min: _Optional[int] = ..., max: _Optional[int] = ..., identifier: _Optional[str] = ...) -> None: ...

class SizeQuery(_message.Message):
    __slots__ = ("id", "name", "description", "labels")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    labels: _common_pb2.Labels
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ...) -> None: ...
