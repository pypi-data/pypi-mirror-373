import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from metalstack.api.v2 import filesystem_pb2 as _filesystem_pb2
from metalstack.api.v2 import image_pb2 as _image_pb2
from metalstack.api.v2 import network_pb2 as _network_pb2
from metalstack.api.v2 import partition_pb2 as _partition_pb2
from metalstack.api.v2 import size_pb2 as _size_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IPProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IP_PROTOCOL_UNSPECIFIED: _ClassVar[IPProtocol]
    IP_PROTOCOL_TCP: _ClassVar[IPProtocol]
    IP_PROTOCOL_UDP: _ClassVar[IPProtocol]

class MachineState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MACHINE_STATE_UNSPECIFIED: _ClassVar[MachineState]
    MACHINE_STATE_RESERVED: _ClassVar[MachineState]
    MACHINE_STATE_LOCKED: _ClassVar[MachineState]
    MACHINE_STATE_AVAILABLE: _ClassVar[MachineState]

class MachineProvisioningEventState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MACHINE_PROVISIONING_EVENT_STATE_UNSPECIFIED: _ClassVar[MachineProvisioningEventState]
    MACHINE_PROVISIONING_EVENT_STATE_CRASHLOOP: _ClassVar[MachineProvisioningEventState]
    MACHINE_PROVISIONING_EVENT_STATE_FAILED_RECLAIM: _ClassVar[MachineProvisioningEventState]

class MachineProvisioningEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MACHINE_PROVISIONING_EVENT_TYPE_UNSPECIFIED: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_ALIVE: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_CRASHED: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_PXE_BOOTING: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_PLANNED_REBOOT: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_PREPARING: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_REGISTERING: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_WAITING: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_INSTALLING: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_BOOTING_NEW_KERNEL: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_PHONED_HOME: _ClassVar[MachineProvisioningEventType]
    MACHINE_PROVISIONING_EVENT_TYPE_MACHINE_RECLAIM: _ClassVar[MachineProvisioningEventType]

class MachineLiveliness(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MACHINE_LIVELINESS_UNSPECIFIED: _ClassVar[MachineLiveliness]
    MACHINE_LIVELINESS_ALIVE: _ClassVar[MachineLiveliness]
    MACHINE_LIVELINESS_DEAD: _ClassVar[MachineLiveliness]
    MACHINE_LIVELINESS_UNKNOWN: _ClassVar[MachineLiveliness]

class MachineAllocationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MACHINE_ALLOCATION_TYPE_UNSPECIFIED: _ClassVar[MachineAllocationType]
    MACHINE_ALLOCATION_TYPE_MACHINE: _ClassVar[MachineAllocationType]
    MACHINE_ALLOCATION_TYPE_FIREWALL: _ClassVar[MachineAllocationType]
IP_PROTOCOL_UNSPECIFIED: IPProtocol
IP_PROTOCOL_TCP: IPProtocol
IP_PROTOCOL_UDP: IPProtocol
MACHINE_STATE_UNSPECIFIED: MachineState
MACHINE_STATE_RESERVED: MachineState
MACHINE_STATE_LOCKED: MachineState
MACHINE_STATE_AVAILABLE: MachineState
MACHINE_PROVISIONING_EVENT_STATE_UNSPECIFIED: MachineProvisioningEventState
MACHINE_PROVISIONING_EVENT_STATE_CRASHLOOP: MachineProvisioningEventState
MACHINE_PROVISIONING_EVENT_STATE_FAILED_RECLAIM: MachineProvisioningEventState
MACHINE_PROVISIONING_EVENT_TYPE_UNSPECIFIED: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_ALIVE: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_CRASHED: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_PXE_BOOTING: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_PLANNED_REBOOT: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_PREPARING: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_REGISTERING: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_WAITING: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_INSTALLING: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_BOOTING_NEW_KERNEL: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_PHONED_HOME: MachineProvisioningEventType
MACHINE_PROVISIONING_EVENT_TYPE_MACHINE_RECLAIM: MachineProvisioningEventType
MACHINE_LIVELINESS_UNSPECIFIED: MachineLiveliness
MACHINE_LIVELINESS_ALIVE: MachineLiveliness
MACHINE_LIVELINESS_DEAD: MachineLiveliness
MACHINE_LIVELINESS_UNKNOWN: MachineLiveliness
MACHINE_ALLOCATION_TYPE_UNSPECIFIED: MachineAllocationType
MACHINE_ALLOCATION_TYPE_MACHINE: MachineAllocationType
MACHINE_ALLOCATION_TYPE_FIREWALL: MachineAllocationType

class MachineServiceGetRequest(_message.Message):
    __slots__ = ("uuid", "project")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    project: str
    def __init__(self, uuid: _Optional[str] = ..., project: _Optional[str] = ...) -> None: ...

class MachineServiceGetResponse(_message.Message):
    __slots__ = ("machine",)
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    machine: Machine
    def __init__(self, machine: _Optional[_Union[Machine, _Mapping]] = ...) -> None: ...

class MachineServiceCreateRequest(_message.Message):
    __slots__ = ("project", "uuid", "name", "description", "hostname", "partition", "size", "image", "filesystem_layout", "ssh_public_keys", "userdata", "labels", "networks", "ips", "placement_tags", "dns_server", "ntp_server", "allocation_type", "firewall_spec")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    SSH_PUBLIC_KEYS_FIELD_NUMBER: _ClassVar[int]
    USERDATA_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    IPS_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_TAGS_FIELD_NUMBER: _ClassVar[int]
    DNS_SERVER_FIELD_NUMBER: _ClassVar[int]
    NTP_SERVER_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIREWALL_SPEC_FIELD_NUMBER: _ClassVar[int]
    project: str
    uuid: str
    name: str
    description: str
    hostname: str
    partition: str
    size: str
    image: str
    filesystem_layout: str
    ssh_public_keys: _containers.RepeatedScalarFieldContainer[str]
    userdata: str
    labels: _common_pb2.Labels
    networks: _containers.RepeatedCompositeFieldContainer[MachineAllocationNetwork]
    ips: _containers.RepeatedScalarFieldContainer[str]
    placement_tags: _containers.RepeatedScalarFieldContainer[str]
    dns_server: _containers.RepeatedCompositeFieldContainer[_partition_pb2.DNSServer]
    ntp_server: _containers.RepeatedCompositeFieldContainer[_partition_pb2.NTPServer]
    allocation_type: MachineAllocationType
    firewall_spec: FirewallSpec
    def __init__(self, project: _Optional[str] = ..., uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., hostname: _Optional[str] = ..., partition: _Optional[str] = ..., size: _Optional[str] = ..., image: _Optional[str] = ..., filesystem_layout: _Optional[str] = ..., ssh_public_keys: _Optional[_Iterable[str]] = ..., userdata: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ..., networks: _Optional[_Iterable[_Union[MachineAllocationNetwork, _Mapping]]] = ..., ips: _Optional[_Iterable[str]] = ..., placement_tags: _Optional[_Iterable[str]] = ..., dns_server: _Optional[_Iterable[_Union[_partition_pb2.DNSServer, _Mapping]]] = ..., ntp_server: _Optional[_Iterable[_Union[_partition_pb2.NTPServer, _Mapping]]] = ..., allocation_type: _Optional[_Union[MachineAllocationType, str]] = ..., firewall_spec: _Optional[_Union[FirewallSpec, _Mapping]] = ...) -> None: ...

class FirewallSpec(_message.Message):
    __slots__ = ("firewall_rules",)
    FIREWALL_RULES_FIELD_NUMBER: _ClassVar[int]
    firewall_rules: FirewallRules
    def __init__(self, firewall_rules: _Optional[_Union[FirewallRules, _Mapping]] = ...) -> None: ...

class MachineServiceCreateResponse(_message.Message):
    __slots__ = ("machine",)
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    machine: Machine
    def __init__(self, machine: _Optional[_Union[Machine, _Mapping]] = ...) -> None: ...

class MachineServiceUpdateRequest(_message.Message):
    __slots__ = ("uuid", "project", "description", "labels", "ssh_public_keys")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    SSH_PUBLIC_KEYS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    project: str
    description: str
    labels: _common_pb2.UpdateLabels
    ssh_public_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uuid: _Optional[str] = ..., project: _Optional[str] = ..., description: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.UpdateLabels, _Mapping]] = ..., ssh_public_keys: _Optional[_Iterable[str]] = ...) -> None: ...

class MachineServiceUpdateResponse(_message.Message):
    __slots__ = ("machine",)
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    machine: Machine
    def __init__(self, machine: _Optional[_Union[Machine, _Mapping]] = ...) -> None: ...

class MachineServiceListRequest(_message.Message):
    __slots__ = ("project", "query")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    project: str
    query: MachineQuery
    def __init__(self, project: _Optional[str] = ..., query: _Optional[_Union[MachineQuery, _Mapping]] = ...) -> None: ...

class MachineServiceListResponse(_message.Message):
    __slots__ = ("machines",)
    MACHINES_FIELD_NUMBER: _ClassVar[int]
    machines: _containers.RepeatedCompositeFieldContainer[Machine]
    def __init__(self, machines: _Optional[_Iterable[_Union[Machine, _Mapping]]] = ...) -> None: ...

class MachineServiceDeleteRequest(_message.Message):
    __slots__ = ("uuid", "project")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    project: str
    def __init__(self, uuid: _Optional[str] = ..., project: _Optional[str] = ...) -> None: ...

class MachineServiceDeleteResponse(_message.Message):
    __slots__ = ("machine",)
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    machine: Machine
    def __init__(self, machine: _Optional[_Union[Machine, _Mapping]] = ...) -> None: ...

class Machine(_message.Message):
    __slots__ = ("uuid", "meta", "partition", "rack", "size", "hardware", "bios", "allocation", "status", "recent_provisioning_events")
    UUID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    RACK_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    BIOS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RECENT_PROVISIONING_EVENTS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    meta: _common_pb2.Meta
    partition: _partition_pb2.Partition
    rack: str
    size: _size_pb2.Size
    hardware: MachineHardware
    bios: MachineBios
    allocation: MachineAllocation
    status: MachineStatus
    recent_provisioning_events: MachineRecentProvisioningEvents
    def __init__(self, uuid: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., partition: _Optional[_Union[_partition_pb2.Partition, _Mapping]] = ..., rack: _Optional[str] = ..., size: _Optional[_Union[_size_pb2.Size, _Mapping]] = ..., hardware: _Optional[_Union[MachineHardware, _Mapping]] = ..., bios: _Optional[_Union[MachineBios, _Mapping]] = ..., allocation: _Optional[_Union[MachineAllocation, _Mapping]] = ..., status: _Optional[_Union[MachineStatus, _Mapping]] = ..., recent_provisioning_events: _Optional[_Union[MachineRecentProvisioningEvents, _Mapping]] = ...) -> None: ...

class MachineStatus(_message.Message):
    __slots__ = ("condition", "led_state", "liveliness", "metal_hammer_version")
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    LED_STATE_FIELD_NUMBER: _ClassVar[int]
    LIVELINESS_FIELD_NUMBER: _ClassVar[int]
    METAL_HAMMER_VERSION_FIELD_NUMBER: _ClassVar[int]
    condition: MachineCondition
    led_state: MachineChassisIdentifyLEDState
    liveliness: MachineLiveliness
    metal_hammer_version: str
    def __init__(self, condition: _Optional[_Union[MachineCondition, _Mapping]] = ..., led_state: _Optional[_Union[MachineChassisIdentifyLEDState, _Mapping]] = ..., liveliness: _Optional[_Union[MachineLiveliness, str]] = ..., metal_hammer_version: _Optional[str] = ...) -> None: ...

class MachineCondition(_message.Message):
    __slots__ = ("state", "description", "issuer")
    STATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    state: MachineState
    description: str
    issuer: str
    def __init__(self, state: _Optional[_Union[MachineState, str]] = ..., description: _Optional[str] = ..., issuer: _Optional[str] = ...) -> None: ...

class MachineAllocation(_message.Message):
    __slots__ = ("uuid", "meta", "name", "description", "created_by", "project", "image", "filesystem_layout", "networks", "hostname", "ssh_public_keys", "userdata", "allocation_type", "firewall_rules", "dns_server", "ntp_server", "vpn")
    UUID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    SSH_PUBLIC_KEYS_FIELD_NUMBER: _ClassVar[int]
    USERDATA_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIREWALL_RULES_FIELD_NUMBER: _ClassVar[int]
    DNS_SERVER_FIELD_NUMBER: _ClassVar[int]
    NTP_SERVER_FIELD_NUMBER: _ClassVar[int]
    VPN_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    meta: _common_pb2.Meta
    name: str
    description: str
    created_by: str
    project: str
    image: _image_pb2.Image
    filesystem_layout: _filesystem_pb2.FilesystemLayout
    networks: _containers.RepeatedCompositeFieldContainer[MachineNetwork]
    hostname: str
    ssh_public_keys: _containers.RepeatedScalarFieldContainer[str]
    userdata: str
    allocation_type: MachineAllocationType
    firewall_rules: FirewallRules
    dns_server: _containers.RepeatedCompositeFieldContainer[_partition_pb2.DNSServer]
    ntp_server: _containers.RepeatedCompositeFieldContainer[_partition_pb2.NTPServer]
    vpn: MachineVPN
    def __init__(self, uuid: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_by: _Optional[str] = ..., project: _Optional[str] = ..., image: _Optional[_Union[_image_pb2.Image, _Mapping]] = ..., filesystem_layout: _Optional[_Union[_filesystem_pb2.FilesystemLayout, _Mapping]] = ..., networks: _Optional[_Iterable[_Union[MachineNetwork, _Mapping]]] = ..., hostname: _Optional[str] = ..., ssh_public_keys: _Optional[_Iterable[str]] = ..., userdata: _Optional[str] = ..., allocation_type: _Optional[_Union[MachineAllocationType, str]] = ..., firewall_rules: _Optional[_Union[FirewallRules, _Mapping]] = ..., dns_server: _Optional[_Iterable[_Union[_partition_pb2.DNSServer, _Mapping]]] = ..., ntp_server: _Optional[_Iterable[_Union[_partition_pb2.NTPServer, _Mapping]]] = ..., vpn: _Optional[_Union[MachineVPN, _Mapping]] = ...) -> None: ...

class MachineAllocationNetwork(_message.Message):
    __slots__ = ("network", "no_auto_acquire_ip")
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    NO_AUTO_ACQUIRE_IP_FIELD_NUMBER: _ClassVar[int]
    network: str
    no_auto_acquire_ip: bool
    def __init__(self, network: _Optional[str] = ..., no_auto_acquire_ip: _Optional[bool] = ...) -> None: ...

class FirewallRules(_message.Message):
    __slots__ = ("egress", "ingress")
    EGRESS_FIELD_NUMBER: _ClassVar[int]
    INGRESS_FIELD_NUMBER: _ClassVar[int]
    egress: _containers.RepeatedCompositeFieldContainer[FirewallEgressRule]
    ingress: _containers.RepeatedCompositeFieldContainer[FirewallIngressRule]
    def __init__(self, egress: _Optional[_Iterable[_Union[FirewallEgressRule, _Mapping]]] = ..., ingress: _Optional[_Iterable[_Union[FirewallIngressRule, _Mapping]]] = ...) -> None: ...

class FirewallEgressRule(_message.Message):
    __slots__ = ("protocol", "ports", "to", "comment")
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    protocol: IPProtocol
    ports: _containers.RepeatedScalarFieldContainer[int]
    to: _containers.RepeatedScalarFieldContainer[str]
    comment: str
    def __init__(self, protocol: _Optional[_Union[IPProtocol, str]] = ..., ports: _Optional[_Iterable[int]] = ..., to: _Optional[_Iterable[str]] = ..., comment: _Optional[str] = ...) -> None: ...

class FirewallIngressRule(_message.Message):
    __slots__ = ("protocol", "ports", "to", "comment")
    PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    FROM_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    protocol: IPProtocol
    ports: _containers.RepeatedScalarFieldContainer[int]
    to: _containers.RepeatedScalarFieldContainer[str]
    comment: str
    def __init__(self, protocol: _Optional[_Union[IPProtocol, str]] = ..., ports: _Optional[_Iterable[int]] = ..., to: _Optional[_Iterable[str]] = ..., comment: _Optional[str] = ..., **kwargs) -> None: ...

class MachineNetwork(_message.Message):
    __slots__ = ("network", "prefixes", "destination_prefixes", "ips", "network_type", "nat_type", "vrf", "asn")
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    IPS_FIELD_NUMBER: _ClassVar[int]
    NETWORK_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VRF_FIELD_NUMBER: _ClassVar[int]
    ASN_FIELD_NUMBER: _ClassVar[int]
    network: str
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    ips: _containers.RepeatedScalarFieldContainer[str]
    network_type: _network_pb2.NetworkType
    nat_type: _network_pb2.NATType
    vrf: int
    asn: int
    def __init__(self, network: _Optional[str] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., ips: _Optional[_Iterable[str]] = ..., network_type: _Optional[_Union[_network_pb2.NetworkType, str]] = ..., nat_type: _Optional[_Union[_network_pb2.NATType, str]] = ..., vrf: _Optional[int] = ..., asn: _Optional[int] = ...) -> None: ...

class MachineHardware(_message.Message):
    __slots__ = ("memory", "disks", "cpus", "gpus", "nics")
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    DISKS_FIELD_NUMBER: _ClassVar[int]
    CPUS_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    NICS_FIELD_NUMBER: _ClassVar[int]
    memory: int
    disks: _containers.RepeatedCompositeFieldContainer[MachineBlockDevice]
    cpus: _containers.RepeatedCompositeFieldContainer[MetalCPU]
    gpus: _containers.RepeatedCompositeFieldContainer[MetalGPU]
    nics: _containers.RepeatedCompositeFieldContainer[MachineNic]
    def __init__(self, memory: _Optional[int] = ..., disks: _Optional[_Iterable[_Union[MachineBlockDevice, _Mapping]]] = ..., cpus: _Optional[_Iterable[_Union[MetalCPU, _Mapping]]] = ..., gpus: _Optional[_Iterable[_Union[MetalGPU, _Mapping]]] = ..., nics: _Optional[_Iterable[_Union[MachineNic, _Mapping]]] = ...) -> None: ...

class MetalCPU(_message.Message):
    __slots__ = ("vendor", "model", "cores", "threads")
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    CORES_FIELD_NUMBER: _ClassVar[int]
    THREADS_FIELD_NUMBER: _ClassVar[int]
    vendor: str
    model: str
    cores: int
    threads: int
    def __init__(self, vendor: _Optional[str] = ..., model: _Optional[str] = ..., cores: _Optional[int] = ..., threads: _Optional[int] = ...) -> None: ...

class MetalGPU(_message.Message):
    __slots__ = ("vendor", "model")
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    vendor: str
    model: str
    def __init__(self, vendor: _Optional[str] = ..., model: _Optional[str] = ...) -> None: ...

class MachineNic(_message.Message):
    __slots__ = ("mac", "name", "identifier", "vendor", "model", "speed", "neighbors")
    MAC_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    NEIGHBORS_FIELD_NUMBER: _ClassVar[int]
    mac: str
    name: str
    identifier: str
    vendor: str
    model: str
    speed: int
    neighbors: _containers.RepeatedCompositeFieldContainer[MachineNic]
    def __init__(self, mac: _Optional[str] = ..., name: _Optional[str] = ..., identifier: _Optional[str] = ..., vendor: _Optional[str] = ..., model: _Optional[str] = ..., speed: _Optional[int] = ..., neighbors: _Optional[_Iterable[_Union[MachineNic, _Mapping]]] = ...) -> None: ...

class MachineBlockDevice(_message.Message):
    __slots__ = ("name", "size")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    name: str
    size: int
    def __init__(self, name: _Optional[str] = ..., size: _Optional[int] = ...) -> None: ...

class MachineChassisIdentifyLEDState(_message.Message):
    __slots__ = ("value", "description")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    value: str
    description: str
    def __init__(self, value: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class MachineBios(_message.Message):
    __slots__ = ("version", "vendor", "date")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    version: str
    vendor: str
    date: str
    def __init__(self, version: _Optional[str] = ..., vendor: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class MachineRecentProvisioningEvents(_message.Message):
    __slots__ = ("events", "last_event_time", "last_error_event", "state")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    LAST_EVENT_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_EVENT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[MachineProvisioningEvent]
    last_event_time: _timestamp_pb2.Timestamp
    last_error_event: MachineProvisioningEvent
    state: MachineProvisioningEventState
    def __init__(self, events: _Optional[_Iterable[_Union[MachineProvisioningEvent, _Mapping]]] = ..., last_event_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_error_event: _Optional[_Union[MachineProvisioningEvent, _Mapping]] = ..., state: _Optional[_Union[MachineProvisioningEventState, str]] = ...) -> None: ...

class MachineProvisioningEvent(_message.Message):
    __slots__ = ("time", "event", "message")
    TIME_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    event: MachineProvisioningEventType
    message: str
    def __init__(self, time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., event: _Optional[_Union[MachineProvisioningEventType, str]] = ..., message: _Optional[str] = ...) -> None: ...

class MachineVPN(_message.Message):
    __slots__ = ("control_plane_address", "auth_key", "connected")
    CONTROL_PLANE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    AUTH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONNECTED_FIELD_NUMBER: _ClassVar[int]
    control_plane_address: str
    auth_key: str
    connected: bool
    def __init__(self, control_plane_address: _Optional[str] = ..., auth_key: _Optional[str] = ..., connected: _Optional[bool] = ...) -> None: ...

class MachineQuery(_message.Message):
    __slots__ = ("uuid", "name", "partition", "size", "rack", "labels", "allocation", "network", "nic", "disk", "ipmi", "fru", "hardware", "state")
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    RACK_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_FIELD_NUMBER: _ClassVar[int]
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    NIC_FIELD_NUMBER: _ClassVar[int]
    DISK_FIELD_NUMBER: _ClassVar[int]
    IPMI_FIELD_NUMBER: _ClassVar[int]
    FRU_FIELD_NUMBER: _ClassVar[int]
    HARDWARE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    partition: str
    size: str
    rack: str
    labels: _common_pb2.Labels
    allocation: MachineAllocationQuery
    network: MachineNetworkQuery
    nic: MachineNicQuery
    disk: MachineDiskQuery
    ipmi: MachineIPMIQuery
    fru: MachineFRUQuery
    hardware: MachineHardwareQuery
    state: MachineState
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ..., partition: _Optional[str] = ..., size: _Optional[str] = ..., rack: _Optional[str] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ..., allocation: _Optional[_Union[MachineAllocationQuery, _Mapping]] = ..., network: _Optional[_Union[MachineNetworkQuery, _Mapping]] = ..., nic: _Optional[_Union[MachineNicQuery, _Mapping]] = ..., disk: _Optional[_Union[MachineDiskQuery, _Mapping]] = ..., ipmi: _Optional[_Union[MachineIPMIQuery, _Mapping]] = ..., fru: _Optional[_Union[MachineFRUQuery, _Mapping]] = ..., hardware: _Optional[_Union[MachineHardwareQuery, _Mapping]] = ..., state: _Optional[_Union[MachineState, str]] = ...) -> None: ...

class MachineAllocationQuery(_message.Message):
    __slots__ = ("uuid", "name", "project", "image", "filesystem_layout", "hostname", "allocation_type", "labels")
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    project: str
    image: str
    filesystem_layout: str
    hostname: str
    allocation_type: MachineAllocationType
    labels: _common_pb2.Labels
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ..., project: _Optional[str] = ..., image: _Optional[str] = ..., filesystem_layout: _Optional[str] = ..., hostname: _Optional[str] = ..., allocation_type: _Optional[_Union[MachineAllocationType, str]] = ..., labels: _Optional[_Union[_common_pb2.Labels, _Mapping]] = ...) -> None: ...

class MachineNetworkQuery(_message.Message):
    __slots__ = ("networks", "prefixes", "destination_prefixes", "ips", "vrfs", "asns")
    NETWORKS_FIELD_NUMBER: _ClassVar[int]
    PREFIXES_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_PREFIXES_FIELD_NUMBER: _ClassVar[int]
    IPS_FIELD_NUMBER: _ClassVar[int]
    VRFS_FIELD_NUMBER: _ClassVar[int]
    ASNS_FIELD_NUMBER: _ClassVar[int]
    networks: _containers.RepeatedScalarFieldContainer[str]
    prefixes: _containers.RepeatedScalarFieldContainer[str]
    destination_prefixes: _containers.RepeatedScalarFieldContainer[str]
    ips: _containers.RepeatedScalarFieldContainer[str]
    vrfs: _containers.RepeatedScalarFieldContainer[int]
    asns: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, networks: _Optional[_Iterable[str]] = ..., prefixes: _Optional[_Iterable[str]] = ..., destination_prefixes: _Optional[_Iterable[str]] = ..., ips: _Optional[_Iterable[str]] = ..., vrfs: _Optional[_Iterable[int]] = ..., asns: _Optional[_Iterable[int]] = ...) -> None: ...

class MachineNicQuery(_message.Message):
    __slots__ = ("macs", "names", "neighbor_macs", "neighbor_names")
    MACS_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    NEIGHBOR_MACS_FIELD_NUMBER: _ClassVar[int]
    NEIGHBOR_NAMES_FIELD_NUMBER: _ClassVar[int]
    macs: _containers.RepeatedScalarFieldContainer[str]
    names: _containers.RepeatedScalarFieldContainer[str]
    neighbor_macs: _containers.RepeatedScalarFieldContainer[str]
    neighbor_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, macs: _Optional[_Iterable[str]] = ..., names: _Optional[_Iterable[str]] = ..., neighbor_macs: _Optional[_Iterable[str]] = ..., neighbor_names: _Optional[_Iterable[str]] = ...) -> None: ...

class MachineDiskQuery(_message.Message):
    __slots__ = ("names", "sizes")
    NAMES_FIELD_NUMBER: _ClassVar[int]
    SIZES_FIELD_NUMBER: _ClassVar[int]
    names: _containers.RepeatedScalarFieldContainer[str]
    sizes: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, names: _Optional[_Iterable[str]] = ..., sizes: _Optional[_Iterable[int]] = ...) -> None: ...

class MachineIPMIQuery(_message.Message):
    __slots__ = ("address", "mac", "user", "interface")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MAC_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_FIELD_NUMBER: _ClassVar[int]
    address: str
    mac: str
    user: str
    interface: str
    def __init__(self, address: _Optional[str] = ..., mac: _Optional[str] = ..., user: _Optional[str] = ..., interface: _Optional[str] = ...) -> None: ...

class MachineFRUQuery(_message.Message):
    __slots__ = ("chassis_part_number", "chassis_part_serial", "board_mfg", "board_serial", "board_part_number", "product_manufacturer", "product_part_number", "product_serial")
    CHASSIS_PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CHASSIS_PART_SERIAL_FIELD_NUMBER: _ClassVar[int]
    BOARD_MFG_FIELD_NUMBER: _ClassVar[int]
    BOARD_SERIAL_FIELD_NUMBER: _ClassVar[int]
    BOARD_PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_SERIAL_FIELD_NUMBER: _ClassVar[int]
    chassis_part_number: str
    chassis_part_serial: str
    board_mfg: str
    board_serial: str
    board_part_number: str
    product_manufacturer: str
    product_part_number: str
    product_serial: str
    def __init__(self, chassis_part_number: _Optional[str] = ..., chassis_part_serial: _Optional[str] = ..., board_mfg: _Optional[str] = ..., board_serial: _Optional[str] = ..., board_part_number: _Optional[str] = ..., product_manufacturer: _Optional[str] = ..., product_part_number: _Optional[str] = ..., product_serial: _Optional[str] = ...) -> None: ...

class MachineHardwareQuery(_message.Message):
    __slots__ = ("memory", "cpu_cores")
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    CPU_CORES_FIELD_NUMBER: _ClassVar[int]
    memory: int
    cpu_cores: int
    def __init__(self, memory: _Optional[int] = ..., cpu_cores: _Optional[int] = ...) -> None: ...
