from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import token_pb2 as _token_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TokenServiceListRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: str
    def __init__(self, user: _Optional[str] = ...) -> None: ...

class TokenServiceListResponse(_message.Message):
    __slots__ = ("tokens",)
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[_token_pb2.Token]
    def __init__(self, tokens: _Optional[_Iterable[_Union[_token_pb2.Token, _Mapping]]] = ...) -> None: ...

class TokenServiceRevokeRequest(_message.Message):
    __slots__ = ("uuid", "user")
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user: str
    def __init__(self, uuid: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class TokenServiceRevokeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
