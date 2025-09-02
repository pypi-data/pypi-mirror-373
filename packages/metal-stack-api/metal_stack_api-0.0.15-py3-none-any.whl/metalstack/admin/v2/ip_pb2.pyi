from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import ip_pb2 as _ip_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IPServiceListRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _ip_pb2.IPQuery
    def __init__(self, query: _Optional[_Union[_ip_pb2.IPQuery, _Mapping]] = ...) -> None: ...

class IPServiceListResponse(_message.Message):
    __slots__ = ("ips",)
    IPS_FIELD_NUMBER: _ClassVar[int]
    ips: _containers.RepeatedCompositeFieldContainer[_ip_pb2.IP]
    def __init__(self, ips: _Optional[_Iterable[_Union[_ip_pb2.IP, _Mapping]]] = ...) -> None: ...

class IPServiceIssuesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IPServiceIssuesResponse(_message.Message):
    __slots__ = ("issues",)
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    issues: _containers.RepeatedCompositeFieldContainer[IPIssue]
    def __init__(self, issues: _Optional[_Iterable[_Union[IPIssue, _Mapping]]] = ...) -> None: ...

class IPIssue(_message.Message):
    __slots__ = ("description", "ip")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    description: str
    ip: _ip_pb2.IP
    def __init__(self, description: _Optional[str] = ..., ip: _Optional[_Union[_ip_pb2.IP, _Mapping]] = ...) -> None: ...
