from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NATType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NAT_TYPE_UNSPECIFIED: _ClassVar[NATType]
    NAT_TYPE_NONE: _ClassVar[NATType]
    NAT_TYPE_IPV4_MASQUERADE: _ClassVar[NATType]

class NetworkType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NETWORK_TYPE_UNSPECIFIED: _ClassVar[NetworkType]
    NETWORK_TYPE_EXTERNAL: _ClassVar[NetworkType]
    NETWORK_TYPE_UNDERLAY: _ClassVar[NetworkType]
    NETWORK_TYPE_SUPER: _ClassVar[NetworkType]
    NETWORK_TYPE_SUPER_NAMESPACED: _ClassVar[NetworkType]
    NETWORK_TYPE_CHILD: _ClassVar[NetworkType]
    NETWORK_TYPE_CHILD_SHARED: _ClassVar[NetworkType]

class NetworkAddressFamily(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NETWORK_ADDRESS_FAMILY_UNSPECIFIED: _ClassVar[NetworkAddressFamily]
    NETWORK_ADDRESS_FAMILY_V4: _ClassVar[NetworkAddressFamily]
    NETWORK_ADDRESS_FAMILY_V6: _ClassVar[NetworkAddressFamily]
    NETWORK_ADDRESS_FAMILY_DUAL_STACK: _ClassVar[NetworkAddressFamily]
NAT_TYPE_UNSPECIFIED: NATType
NAT_TYPE_NONE: NATType
NAT_TYPE_IPV4_MASQUERADE: NATType
NETWORK_TYPE_UNSPECIFIED: NetworkType
NETWORK_TYPE_EXTERNAL: NetworkType
NETWORK_TYPE_UNDERLAY: NetworkType
NETWORK_TYPE_SUPER: NetworkType
NETWORK_TYPE_SUPER_NAMESPACED: NetworkType
NETWORK_TYPE_CHILD: NetworkType
NETWORK_TYPE_CHILD_SHARED: NetworkType
NETWORK_ADDRESS_FAMILY_UNSPECIFIED: NetworkAddressFamily
NETWORK_ADDRESS_FAMILY_V4: NetworkAddressFamily
NETWORK_ADDRESS_FAMILY_V6: NetworkAddressFamily
NETWORK_ADDRESS_FAMILY_DUAL_STACK: NetworkAddressFamily

class NetworkServiceGetRequest(_message.Message):
    __slots__ = ("id", "project")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    project: str
    def __init__(self, id: _Optional[str] = ..., project: _Optional[str] = ...) -> None: ...

class NetworkServiceGetResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: Network
    def __init__(self, network: _Optional[_Union[Network, _Mapping]] = ...) -> None: ...

class NetworkServiceCreateRequest(_message.Message):
    __slots__ = ("project", "name", "description", "partition", "labels", "parent_network", "length", "address_family")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    PARENT_NETWORK_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FAMILY_FIELD_NUMBER: _ClassVar[int]
    project: str
    name: str
    description: str
    partition: str
    labels: _common_pb2.Labels
    parent_network: str
    length: ChildPrefixLength
    address_family: NetworkAddressFamily
    def __init__(self, project: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., partition: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ..., parent_network: _Optional[str] = ..., length: _Optional[_Union[ChildPrefixLength, _Mapping]] = ..., address_family: _Optional[_Union[NetworkAddressFamily, str]] = ...) -> None: ...

class NetworkServiceCreateResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: Network
    def __init__(self, network: _Optional[_Union[Network, _Mapping]] = ...) -> None: ...

class NetworkServiceUpdateRequest(_message.Message):
    __slots__ = ("id", "project", "name", "description", "labels")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    project: str
    name: str
    description: str
    labels: _common_pb2.UpdateLabels
    def __init__(self, id: _Optional[str] = ..., project: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.UpdateLabels, _Mapping]] = ...) -> None: ...

class NetworkServiceUpdateResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: Network
    def __init__(self, network: _Optional[_Union[Network, _Mapping]] = ...) -> None: ...

class NetworkServiceListRequest(_message.Message):
    __slots__ = ("project", "query")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    project: str
    query: NetworkQuery
    def __init__(self, project: _Optional[str] = ..., query: _Optional[_Union[NetworkQuery, _Mapping]] = ...) -> None: ...

class NetworkServiceListResponse(_message.Message):
    __slots__ = ("networks",)
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    networks: _containers.RepeatedCompositeFieldContainer[Network]
    def __init__(self, networks: _Optional[_Iterable[_Union[Network, _Mapping]]] = ...) -> None: ...

class NetworkServiceListBaseNetworksRequest(_message.Message):
    __slots__ = ("project", "query")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    project: str
    query: NetworkQuery
    def __init__(self, project: _Optional[str] = ..., query: _Optional[_Union[NetworkQuery, _Mapping]] = ...) -> None: ...

class NetworkServiceListBaseNetworksResponse(_message.Message):
    __slots__ = ("networks",)
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    networks: _containers.RepeatedCompositeFieldContainer[Network]
    def __init__(self, networks: _Optional[_Iterable[_Union[Network, _Mapping]]] = ...) -> None: ...

class NetworkServiceDeleteRequest(_message.Message):
    __slots__ = ("id", "project")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    project: str
    def __init__(self, id: _Optional[str] = ..., project: _Optional[str] = ...) -> None: ...

class NetworkServiceDeleteResponse(_message.Message):
    __slots__ = ("network",)
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    network: Network
    def __init__(self, network: _Optional[_Union[Network, _Mapping]] = ...) -> None: ...

class Network(_message.Message):
    __slots__ = ("id", "meta", "name", "description", "partition", "project", "namespace", "prefixes", "destination_prefixes", "default_child_prefix_length", "min_child_prefix_length", "type", "nat_type", "vrf", "parent_network", "additional_announcable_cidrs", "consumption")
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MIN_CHILD_PREFIX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VRF_FIELD_NUMBER: _ClassVar[int]
    PARENT_NETWORK_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_ANNOUNCABLE_CIDRS_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    meta: _common_pb2.Meta
    name: str
    description: str
    partition: str
    project: str
    namespace: str
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    default_child_prefix_length: ChildPrefixLength
    min_child_prefix_length: ChildPrefixLength
    type: NetworkType
    nat_type: NATType
    vrf: int
    parent_network: str
    additional_announcable_cidrs: _containers.RepeatedScalarFieldContainer[str]
    consumption: NetworkConsumption
    def __init__(self, id: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., partition: _Optional[str] = ..., project: _Optional[str] = ..., namespace: _Optional[str] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., default_child_prefix_length: _Optional[_Union[ChildPrefixLength, _Mapping]] = ..., min_child_prefix_length: _Optional[_Union[ChildPrefixLength, _Mapping]] = ..., type: _Optional[_Union[NetworkType, str]] = ..., nat_type: _Optional[_Union[NATType, str]] = ..., vrf: _Optional[int] = ..., parent_network: _Optional[str] = ..., additional_announcable_cidrs: _Optional[_Iterable[str]] = ..., consumption: _Optional[_Union[NetworkConsumption, _Mapping]] = ...) -> None: ...

class NetworkQuery(_message.Message):
    __slots__ = ("id", "name", "description", "partition", "project", "namespace", "prefixes", "destination_prefixes", "vrf", "parent_network", "address_family", "type", "nat_type", "labels")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    VRF_FIELD_NUMBER: _ClassVar[int]
    PARENT_NETWORK_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FAMILY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    partition: str
    project: str
    namespace: str
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    vrf: int
    parent_network: str
    address_family: NetworkAddressFamily
    type: NetworkType
    nat_type: NATType
    labels: _common_pb2.Labels
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., partition: _Optional[str] = ..., project: _Optional[str] = ..., namespace: _Optional[str] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., vrf: _Optional[int] = ..., parent_network: _Optional[str] = ..., address_family: _Optional[_Union[NetworkAddressFamily, str]] = ..., type: _Optional[_Union[NetworkType, str]] = ..., nat_type: _Optional[_Union[NATType, str]] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ...) -> None: ...

class ChildPrefixLength(_message.Message):
    __slots__ = ("ipv4", "ipv6")
    IPV4_FIELD_NUMBER: _ClassVar[int]
    IPV6_FIELD_NUMBER: _ClassVar[int]
    ipv4: int
    ipv6: int
    def __init__(self, ipv4: _Optional[int] = ..., ipv6: _Optional[int] = ...) -> None: ...

class NetworkConsumption(_message.Message):
    __slots__ = ("ipv4", "ipv6")
    IPV4_FIELD_NUMBER: _ClassVar[int]
    IPV6_FIELD_NUMBER: _ClassVar[int]
    ipv4: NetworkUsage
    ipv6: NetworkUsage
    def __init__(self, ipv4: _Optional[_Union[NetworkUsage, _Mapping]] = ..., ipv6: _Optional[_Union[NetworkUsage, _Mapping]] = ...) -> None: ...

class NetworkUsage(_message.Message):
    __slots__ = ("available_ips", "used_ips", "available_prefixes", "used_prefixes")
    AVAILABLE_IPS_FIELD_NUMBER: _ClassVar[int]
    USED_IPS_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    USED_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    available_ips: int
    used_ips: int
    available_prefixes: int
    used_prefixes: int
    def __init__(self, available_ips: _Optional[int] = ..., used_ips: _Optional[int] = ..., available_prefixes: _Optional[int] = ..., used_prefixes: _Optional[int] = ...) -> None: ...
