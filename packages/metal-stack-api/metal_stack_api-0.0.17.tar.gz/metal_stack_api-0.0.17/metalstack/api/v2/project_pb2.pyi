import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Project(_message.Message):
    __slots__ = ("uuid", "meta", "name", "description", "tenant", "avatar_url")
    UUID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    meta: _common_pb2.Meta
    name: str
    description: str
    tenant: str
    avatar_url: str
    def __init__(self, uuid: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., tenant: _Optional[str] = ..., avatar_url: _Optional[str] = ...) -> None: ...

class ProjectMember(_message.Message):
    __slots__ = ("id", "role", "inherited_membership", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    INHERITED_MEMBERSHIP_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    role: _common_pb2.ProjectRole
    inherited_membership: bool
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., role: _Optional[_Union[_common_pb2.ProjectRole, str]] = ..., inherited_membership: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ProjectInvite(_message.Message):
    __slots__ = ("secret", "project", "role", "joined", "project_name", "tenant", "tenant_name", "expires_at", "joined_at")
    SECRET_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    JOINED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    JOINED_AT_FIELD_NUMBER: _ClassVar[int]
    secret: str
    project: str
    role: _common_pb2.ProjectRole
    joined: bool
    project_name: str
    tenant: str
    tenant_name: str
    expires_at: _timestamp_pb2.Timestamp
    joined_at: _timestamp_pb2.Timestamp
    def __init__(self, secret: _Optional[str] = ..., project: _Optional[str] = ..., role: _Optional[_Union[_common_pb2.ProjectRole, str]] = ..., joined: _Optional[bool] = ..., project_name: _Optional[str] = ..., tenant: _Optional[str] = ..., tenant_name: _Optional[str] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., joined_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ProjectServiceListRequest(_message.Message):
    __slots__ = ("id", "name", "tenant")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    tenant: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., tenant: _Optional[str] = ...) -> None: ...

class ProjectServiceListResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[Project]
    def __init__(self, projects: _Optional[_Iterable[_Union[Project, _Mapping]]] = ...) -> None: ...

class ProjectServiceGetRequest(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: str
    def __init__(self, project: _Optional[str] = ...) -> None: ...

class ProjectServiceGetResponse(_message.Message):
    __slots__ = ("project", "project_members")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    project: Project
    project_members: _containers.RepeatedCompositeFieldContainer[ProjectMember]
    def __init__(self, project: _Optional[_Union[Project, _Mapping]] = ..., project_members: _Optional[_Iterable[_Union[ProjectMember, _Mapping]]] = ...) -> None: ...

class ProjectServiceCreateRequest(_message.Message):
    __slots__ = ("login", "name", "description", "avatar_url", "labels")
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    login: str
    name: str
    description: str
    avatar_url: str
    labels: _common_pb2.Labels
    def __init__(self, login: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., avatar_url: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ...) -> None: ...

class ProjectServiceCreateResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: Project
    def __init__(self, project: _Optional[_Union[Project, _Mapping]] = ...) -> None: ...

class ProjectServiceDeleteRequest(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: str
    def __init__(self, project: _Optional[str] = ...) -> None: ...

class ProjectServiceDeleteResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: Project
    def __init__(self, project: _Optional[_Union[Project, _Mapping]] = ...) -> None: ...

class ProjectServiceUpdateRequest(_message.Message):
    __slots__ = ("project", "name", "description", "avatar_url", "labels")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    AVATAR_URL_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    project: str
    name: str
    description: str
    avatar_url: str
    labels: _common_pb2.UpdateLabels
    def __init__(self, project: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., avatar_url: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.UpdateLabels, _Mapping]] = ...) -> None: ...

class ProjectServiceUpdateResponse(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: Project
    def __init__(self, project: _Optional[_Union[Project, _Mapping]] = ...) -> None: ...

class ProjectServiceInviteRequest(_message.Message):
    __slots__ = ("project", "role")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project: str
    role: _common_pb2.ProjectRole
    def __init__(self, project: _Optional[str] = ..., role: _Optional[_Union[_common_pb2.ProjectRole, str]] = ...) -> None: ...

class ProjectServiceInviteResponse(_message.Message):
    __slots__ = ("invite",)
    INVITE_FIELD_NUMBER: _ClassVar[int]
    invite: ProjectInvite
    def __init__(self, invite: _Optional[_Union[ProjectInvite, _Mapping]] = ...) -> None: ...

class ProjectServiceInvitesListRequest(_message.Message):
    __slots__ = ("project",)
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    project: str
    def __init__(self, project: _Optional[str] = ...) -> None: ...

class ProjectServiceInvitesListResponse(_message.Message):
    __slots__ = ("invites",)
    INVITES_FIELD_NUMBER: _ClassVar[int]
    invites: _containers.RepeatedCompositeFieldContainer[ProjectInvite]
    def __init__(self, invites: _Optional[_Iterable[_Union[ProjectInvite, _Mapping]]] = ...) -> None: ...

class ProjectServiceInviteGetRequest(_message.Message):
    __slots__ = ("secret",)
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: str
    def __init__(self, secret: _Optional[str] = ...) -> None: ...

class ProjectServiceInviteGetResponse(_message.Message):
    __slots__ = ("invite",)
    INVITE_FIELD_NUMBER: _ClassVar[int]
    invite: ProjectInvite
    def __init__(self, invite: _Optional[_Union[ProjectInvite, _Mapping]] = ...) -> None: ...

class ProjectServiceRemoveMemberRequest(_message.Message):
    __slots__ = ("project", "member")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    project: str
    member: str
    def __init__(self, project: _Optional[str] = ..., member: _Optional[str] = ...) -> None: ...

class ProjectServiceRemoveMemberResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ProjectServiceUpdateMemberRequest(_message.Message):
    __slots__ = ("project", "member", "role")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    project: str
    member: str
    role: _common_pb2.ProjectRole
    def __init__(self, project: _Optional[str] = ..., member: _Optional[str] = ..., role: _Optional[_Union[_common_pb2.ProjectRole, str]] = ...) -> None: ...

class ProjectServiceUpdateMemberResponse(_message.Message):
    __slots__ = ("project_member",)
    PROJECT_MEMBER_FIELD_NUMBER: _ClassVar[int]
    project_member: ProjectMember
    def __init__(self, project_member: _Optional[_Union[ProjectMember, _Mapping]] = ...) -> None: ...

class ProjectServiceInviteAcceptRequest(_message.Message):
    __slots__ = ("secret",)
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: str
    def __init__(self, secret: _Optional[str] = ...) -> None: ...

class ProjectServiceInviteAcceptResponse(_message.Message):
    __slots__ = ("project", "project_name")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    project: str
    project_name: str
    def __init__(self, project: _Optional[str] = ..., project_name: _Optional[str] = ...) -> None: ...

class ProjectServiceInviteDeleteRequest(_message.Message):
    __slots__ = ("project", "secret")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    project: str
    secret: str
    def __init__(self, project: _Optional[str] = ..., secret: _Optional[str] = ...) -> None: ...

class ProjectServiceInviteDeleteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
