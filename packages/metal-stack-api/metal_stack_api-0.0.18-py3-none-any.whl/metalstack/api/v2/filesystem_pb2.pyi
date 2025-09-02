from buf.validate import validate_pb2 as _validate_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LVMType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LVM_TYPE_UNSPECIFIED: _ClassVar[LVMType]
    LVM_TYPE_LINEAR: _ClassVar[LVMType]
    LVM_TYPE_STRIPED: _ClassVar[LVMType]
    LVM_TYPE_RAID1: _ClassVar[LVMType]

class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMAT_UNSPECIFIED: _ClassVar[Format]
    FORMAT_VFAT: _ClassVar[Format]
    FORMAT_EXT3: _ClassVar[Format]
    FORMAT_EXT4: _ClassVar[Format]
    FORMAT_SWAP: _ClassVar[Format]
    FORMAT_TMPFS: _ClassVar[Format]
    FORMAT_NONE: _ClassVar[Format]

class GPTType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GPT_TYPE_UNSPECIFIED: _ClassVar[GPTType]
    GPT_TYPE_BOOT: _ClassVar[GPTType]
    GPT_TYPE_LINUX: _ClassVar[GPTType]
    GPT_TYPE_LINUX_RAID: _ClassVar[GPTType]
    GPT_TYPE_LINUX_LVM: _ClassVar[GPTType]

class RaidLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RAID_LEVEL_UNSPECIFIED: _ClassVar[RaidLevel]
    RAID_LEVEL_0: _ClassVar[RaidLevel]
    RAID_LEVEL_1: _ClassVar[RaidLevel]
LVM_TYPE_UNSPECIFIED: LVMType
LVM_TYPE_LINEAR: LVMType
LVM_TYPE_STRIPED: LVMType
LVM_TYPE_RAID1: LVMType
FORMAT_UNSPECIFIED: Format
FORMAT_VFAT: Format
FORMAT_EXT3: Format
FORMAT_EXT4: Format
FORMAT_SWAP: Format
FORMAT_TMPFS: Format
FORMAT_NONE: Format
GPT_TYPE_UNSPECIFIED: GPTType
GPT_TYPE_BOOT: GPTType
GPT_TYPE_LINUX: GPTType
GPT_TYPE_LINUX_RAID: GPTType
GPT_TYPE_LINUX_LVM: GPTType
RAID_LEVEL_UNSPECIFIED: RaidLevel
RAID_LEVEL_0: RaidLevel
RAID_LEVEL_1: RaidLevel

class FilesystemServiceGetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class FilesystemServiceListRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class FilesystemServiceGetResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceListResponse(_message.Message):
    __slots__ = ("filesystem_layouts",)
    FILESYSTEM_LAYOUTS_FIELD_NUMBER: _ClassVar[int]
    filesystem_layouts: _containers.RepeatedCompositeFieldContainer[FilesystemLayout]
    def __init__(self, filesystem_layouts: _Optional[_Iterable[_Union[FilesystemLayout, _Mapping]]] = ...) -> None: ...

class FilesystemServiceMatchRequest(_message.Message):
    __slots__ = ("size_and_image", "machine_and_filesystemlayout")
    SIZE_AND_IMAGE_FIELD_NUMBER: _ClassVar[int]
    MACHINE_AND_FILESYSTEMLAYOUT_FIELD_NUMBER: _ClassVar[int]
    size_and_image: MatchImageAndSize
    machine_and_filesystemlayout: MatchMachine
    def __init__(self, size_and_image: _Optional[_Union[MatchImageAndSize, _Mapping]] = ..., machine_and_filesystemlayout: _Optional[_Union[MatchMachine, _Mapping]] = ...) -> None: ...

class MatchImageAndSize(_message.Message):
    __slots__ = ("size", "image")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    size: str
    image: str
    def __init__(self, size: _Optional[str] = ..., image: _Optional[str] = ...) -> None: ...

class MatchMachine(_message.Message):
    __slots__ = ("machine", "filesystem_layout")
    MACHINE_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    machine: str
    filesystem_layout: str
    def __init__(self, machine: _Optional[str] = ..., filesystem_layout: _Optional[str] = ...) -> None: ...

class FilesystemServiceTryResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemServiceMatchResponse(_message.Message):
    __slots__ = ("filesystem_layout",)
    FILESYSTEM_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    filesystem_layout: FilesystemLayout
    def __init__(self, filesystem_layout: _Optional[_Union[FilesystemLayout, _Mapping]] = ...) -> None: ...

class FilesystemLayout(_message.Message):
    __slots__ = ("id", "meta", "name", "description", "filesystems", "disks", "raid", "volume_groups", "logical_volumes", "constraints")
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEMS_FIELD_NUMBER: _ClassVar[int]
    DISKS_FIELD_NUMBER: _ClassVar[int]
    RAID_FIELD_NUMBER: _ClassVar[int]
    VOLUME_GROUPS_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_VOLUMES_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINTS_FIELD_NUMBER: _ClassVar[int]
    id: str
    meta: _common_pb2.Meta
    name: str
    description: str
    filesystems: _containers.RepeatedCompositeFieldContainer[Filesystem]
    disks: _containers.RepeatedCompositeFieldContainer[Disk]
    raid: _containers.RepeatedCompositeFieldContainer[Raid]
    volume_groups: _containers.RepeatedCompositeFieldContainer[VolumeGroup]
    logical_volumes: _containers.RepeatedCompositeFieldContainer[LogicalVolume]
    constraints: FilesystemLayoutConstraints
    def __init__(self, id: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., filesystems: _Optional[_Iterable[_Union[Filesystem, _Mapping]]] = ..., disks: _Optional[_Iterable[_Union[Disk, _Mapping]]] = ..., raid: _Optional[_Iterable[_Union[Raid, _Mapping]]] = ..., volume_groups: _Optional[_Iterable[_Union[VolumeGroup, _Mapping]]] = ..., logical_volumes: _Optional[_Iterable[_Union[LogicalVolume, _Mapping]]] = ..., constraints: _Optional[_Union[FilesystemLayoutConstraints, _Mapping]] = ...) -> None: ...

class FilesystemLayoutConstraints(_message.Message):
    __slots__ = ("sizes", "images")
    class ImagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SIZES_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    sizes: _containers.RepeatedScalarFieldContainer[str]
    images: _containers.ScalarMap[str, str]
    def __init__(self, sizes: _Optional[_Iterable[str]] = ..., images: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Filesystem(_message.Message):
    __slots__ = ("device", "format", "name", "description", "path", "label", "mount_options", "create_options")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MOUNT_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    device: str
    format: Format
    name: str
    description: str
    path: str
    label: str
    mount_options: _containers.RepeatedScalarFieldContainer[str]
    create_options: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, device: _Optional[str] = ..., format: _Optional[_Union[Format, str]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., path: _Optional[str] = ..., label: _Optional[str] = ..., mount_options: _Optional[_Iterable[str]] = ..., create_options: _Optional[_Iterable[str]] = ...) -> None: ...

class Disk(_message.Message):
    __slots__ = ("device", "partitions")
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    device: str
    partitions: _containers.RepeatedCompositeFieldContainer[DiskPartition]
    def __init__(self, device: _Optional[str] = ..., partitions: _Optional[_Iterable[_Union[DiskPartition, _Mapping]]] = ...) -> None: ...

class Raid(_message.Message):
    __slots__ = ("array_name", "devices", "level", "create_options", "spares")
    ARRAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    CREATE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SPARES_FIELD_NUMBER: _ClassVar[int]
    array_name: str
    devices: _containers.RepeatedScalarFieldContainer[str]
    level: RaidLevel
    create_options: _containers.RepeatedScalarFieldContainer[str]
    spares: int
    def __init__(self, array_name: _Optional[str] = ..., devices: _Optional[_Iterable[str]] = ..., level: _Optional[_Union[RaidLevel, str]] = ..., create_options: _Optional[_Iterable[str]] = ..., spares: _Optional[int] = ...) -> None: ...

class DiskPartition(_message.Message):
    __slots__ = ("number", "label", "size", "gpt_type")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    GPT_TYPE_FIELD_NUMBER: _ClassVar[int]
    number: int
    label: str
    size: int
    gpt_type: GPTType
    def __init__(self, number: _Optional[int] = ..., label: _Optional[str] = ..., size: _Optional[int] = ..., gpt_type: _Optional[_Union[GPTType, str]] = ...) -> None: ...

class VolumeGroup(_message.Message):
    __slots__ = ("name", "devices", "tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    devices: _containers.RepeatedScalarFieldContainer[str]
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., devices: _Optional[_Iterable[str]] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class LogicalVolume(_message.Message):
    __slots__ = ("name", "volume_group", "size", "lvm_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_GROUP_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LVM_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    volume_group: str
    size: int
    lvm_type: LVMType
    def __init__(self, name: _Optional[str] = ..., volume_group: _Optional[str] = ..., size: _Optional[int] = ..., lvm_type: _Optional[_Union[LVMType, str]] = ...) -> None: ...
