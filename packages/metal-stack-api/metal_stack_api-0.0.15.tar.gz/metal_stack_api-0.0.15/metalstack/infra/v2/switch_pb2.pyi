from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import switch_pb2 as _switch_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchServiceRegisterRequest(_message.Message):
    __slots__ = ("switch",)
    SWITCH_FIELD_NUMBER: _ClassVar[int]
    switch: _switch_pb2.Switch
    def __init__(self, switch: _Optional[_Union[_switch_pb2.Switch, _Mapping]] = ...) -> None: ...

class SwitchServiceRegisterResponse(_message.Message):
    __slots__ = ("switch",)
    SWITCH_FIELD_NUMBER: _ClassVar[int]
    switch: _switch_pb2.Switch
    def __init__(self, switch: _Optional[_Union[_switch_pb2.Switch, _Mapping]] = ...) -> None: ...
