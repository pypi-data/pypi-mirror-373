from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import machine_pb2 as _machine_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MachineServiceGetRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class MachineServiceGetResponse(_message.Message):
    __slots__ = ("machine",)
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    machine: _machine_pb2.Machine
    def __init__(self, machine: _Optional[_Union[_machine_pb2.Machine, _Mapping]] = ...) -> None: ...

class MachineServiceListRequest(_message.Message):
    __slots__ = ("query", "partition")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    query: _machine_pb2.MachineQuery
    partition: str
    def __init__(self, query: _Optional[_Union[_machine_pb2.MachineQuery, _Mapping]] = ..., partition: _Optional[str] = ...) -> None: ...

class MachineServiceListResponse(_message.Message):
    __slots__ = ("machines",)
    MACHINES_FIELD_NUMBER: _ClassVar[int]
    machines: _containers.RepeatedCompositeFieldContainer[_machine_pb2.Machine]
    def __init__(self, machines: _Optional[_Iterable[_Union[_machine_pb2.Machine, _Mapping]]] = ...) -> None: ...
