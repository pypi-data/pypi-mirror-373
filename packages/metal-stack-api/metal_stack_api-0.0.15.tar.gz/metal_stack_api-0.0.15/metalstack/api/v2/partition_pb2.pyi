from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Partition(_message.Message):
    __slots__ = ("id", "meta", "description", "boot_configuration", "dns_server", "ntp_server", "mgmt_service_addresses")
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    BOOT_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DNS_SERVER_FIELD_NUMBER: _ClassVar[int]
    NTP_SERVER_FIELD_NUMBER: _ClassVar[int]
    MGMT_SERVICE_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    id: str
    meta: _common_pb2.Meta
    description: str
    boot_configuration: PartitionBootConfiguration
    dns_server: _containers.RepeatedCompositeFieldContainer[DNSServer]
    ntp_server: _containers.RepeatedCompositeFieldContainer[NTPServer]
    mgmt_service_addresses: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., description: _Optional[str] = ..., boot_configuration: _Optional[_Union[PartitionBootConfiguration, _Mapping]] = ..., dns_server: _Optional[_Iterable[_Union[DNSServer, _Mapping]]] = ..., ntp_server: _Optional[_Iterable[_Union[NTPServer, _Mapping]]] = ..., mgmt_service_addresses: _Optional[_Iterable[str]] = ...) -> None: ...

class PartitionQuery(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class PartitionBootConfiguration(_message.Message):
    __slots__ = ("image_url", "kernel_url", "commandline")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    KERNEL_URL_FIELD_NUMBER: _ClassVar[int]
    COMMANDLINE_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    kernel_url: str
    commandline: str
    def __init__(self, image_url: _Optional[str] = ..., kernel_url: _Optional[str] = ..., commandline: _Optional[str] = ...) -> None: ...

class DNSServer(_message.Message):
    __slots__ = ("ip",)
    IP_FIELD_NUMBER: _ClassVar[int]
    ip: str
    def __init__(self, ip: _Optional[str] = ...) -> None: ...

class NTPServer(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class PartitionServiceGetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class PartitionServiceListRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: PartitionQuery
    def __init__(self, query: _Optional[_Union[PartitionQuery, _Mapping]] = ...) -> None: ...

class PartitionServiceGetResponse(_message.Message):
    __slots__ = ("partition",)
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    partition: Partition
    def __init__(self, partition: _Optional[_Union[Partition, _Mapping]] = ...) -> None: ...

class PartitionServiceListResponse(_message.Message):
    __slots__ = ("partitions",)
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    partitions: _containers.RepeatedCompositeFieldContainer[Partition]
    def __init__(self, partitions: _Optional[_Iterable[_Union[Partition, _Mapping]]] = ...) -> None: ...
