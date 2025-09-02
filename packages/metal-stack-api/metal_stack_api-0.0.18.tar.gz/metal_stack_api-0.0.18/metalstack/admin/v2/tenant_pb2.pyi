from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import tenant_pb2 as _tenant_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TenantServiceCreateRequest(_message.Message):
    __slots__ = ("name", "description", "email", "avatar_url")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    email: str
    avatar_url: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., email: _Optional[str] = ..., avatar_url: _Optional[str] = ...) -> None: ...

class TenantServiceCreateResponse(_message.Message):
    __slots__ = ("tenant",)
    TENANT_FIELD_NUMBER: _ClassVar[int]
    tenant: _tenant_pb2.Tenant
    def __init__(self, tenant: _Optional[_Union[_tenant_pb2.Tenant, _Mapping]] = ...) -> None: ...

class TenantServiceListRequest(_message.Message):
    __slots__ = ("login", "name", "email", "paging")
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PAGING_FIELD_NUMBER: _ClassVar[int]
    login: str
    name: str
    email: str
    paging: _common_pb2.Paging
    def __init__(self, login: _Optional[str] = ..., name: _Optional[str] = ..., email: _Optional[str] = ..., paging: _Optional[_Union[_common_pb2.Paging, _Mapping]] = ...) -> None: ...

class TenantServiceListResponse(_message.Message):
    __slots__ = ("tenants", "next_page")
    TENANTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    tenants: _containers.RepeatedCompositeFieldContainer[_tenant_pb2.Tenant]
    next_page: int
    def __init__(self, tenants: _Optional[_Iterable[_Union[_tenant_pb2.Tenant, _Mapping]]] = ..., next_page: _Optional[int] = ...) -> None: ...
