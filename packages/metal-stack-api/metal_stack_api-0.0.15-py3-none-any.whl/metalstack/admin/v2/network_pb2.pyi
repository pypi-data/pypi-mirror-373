from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import network_pb2 as _network_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NetworkServiceGetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class NetworkServiceGetResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: _network_pb2.Network
    def __init__(self, network: _Optional[_Union[_network_pb2.Network, _Mapping]] = ...) -> None: ...

class NetworkServiceCreateRequest(_message.Message):
    __slots__ = ("id", "name", "description", "partition", "project", "type", "labels", "prefixes", "destination_prefixes", "default_child_prefix_length", "min_child_prefix_length", "nat_type", "vrf", "parent_network", "additional_announcable_cidrs", "length", "address_family")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MIN_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VRF_FIELD_NUMBER: _ClassVar[int]
    PARENT_NETWORK_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ANNOUNCABLE_CIDRS_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FAMILY_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    partition: str
    project: str
    type: _network_pb2.NetworkType
    labels: _common_pb2.Labels
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    default_child_prefix_length: _network_pb2.ChildPrefixLength
    min_child_prefix_length: _network_pb2.ChildPrefixLength
    nat_type: _network_pb2.NATType
    vrf: int
    parent_network: str
    additional_announcable_cidrs: _containers.RepeatedScalarFieldContainer[str]
    length: _network_pb2.ChildPrefixLength
    address_family: _network_pb2.NetworkAddressFamily
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., partition: _Optional[str] = ..., project: _Optional[str] = ..., type: _Optional[_Union[_network_pb2.NetworkType, str]] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., default_child_prefix_length: _Optional[_Union[_network_pb2.ChildPrefixLength, _Mapping]] = ..., min_child_prefix_length: _Optional[_Union[_network_pb2.ChildPrefixLength, _Mapping]] = ..., nat_type: _Optional[_Union[_network_pb2.NATType, str]] = ..., vrf: _Optional[int] = ..., parent_network: _Optional[str] = ..., additional_announcable_cidrs: _Optional[_Iterable[str]] = ..., length: _Optional[_Union[_network_pb2.ChildPrefixLength, _Mapping]] = ..., address_family: _Optional[_Union[_network_pb2.NetworkAddressFamily, str]] = ...) -> None: ...

class NetworkServiceUpdateRequest(_message.Message):
    __slots__ = ("id", "name", "description", "labels", "prefixes", "destination_prefixes", "default_child_prefix_length", "min_child_prefix_length", "nat_type", "additional_announcable_cidrs", "force")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MIN_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ANNOUNCABLE_CIDRS_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    labels: _common_pb2.UpdateLabels
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    default_child_prefix_length: _network_pb2.ChildPrefixLength
    min_child_prefix_length: _network_pb2.ChildPrefixLength
    nat_type: _network_pb2.NATType
    additional_announcable_cidrs: _containers.RepeatedScalarFieldContainer[str]
    force: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.UpdateLabels, _Mapping]] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., default_child_prefix_length: _Optional[_Union[_network_pb2.ChildPrefixLength, _Mapping]] = ..., min_child_prefix_length: _Optional[_Union[_network_pb2.ChildPrefixLength, _Mapping]] = ..., nat_type: _Optional[_Union[_network_pb2.NATType, str]] = ..., additional_announcable_cidrs: _Optional[_Iterable[str]] = ..., force: _Optional[bool] = ...) -> None: ...

class NetworkServiceDeleteRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class NetworkServiceListRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: _network_pb2.NetworkQuery
    def __init__(self, query: _Optional[_Union[_network_pb2.NetworkQuery, _Mapping]] = ...) -> None: ...

class NetworkServiceCreateResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: _network_pb2.Network
    def __init__(self, network: _Optional[_Union[_network_pb2.Network, _Mapping]] = ...) -> None: ...

class NetworkServiceUpdateResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: _network_pb2.Network
    def __init__(self, network: _Optional[_Union[_network_pb2.Network, _Mapping]] = ...) -> None: ...

class NetworkServiceDeleteResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: _network_pb2.Network
    def __init__(self, network: _Optional[_Union[_network_pb2.Network, _Mapping]] = ...) -> None: ...

class NetworkServiceListResponse(_message.Message):
    __slots__ = ("networks",)
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    networks: _containers.RepeatedCompositeFieldContainer[_network_pb2.Network]
    def __init__(self, networks: _Optional[_Iterable[_Union[_network_pb2.Network, _Mapping]]] = ...) -> None: ...
