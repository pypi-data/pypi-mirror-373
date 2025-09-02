from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import filesystem_pb2 as _filesystem_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FilesystemServiceCreateRequest(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceCreateResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceUpdateRequest(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceUpdateResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceDeleteRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class FilesystemServiceDeleteResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ...) -> None: ...
