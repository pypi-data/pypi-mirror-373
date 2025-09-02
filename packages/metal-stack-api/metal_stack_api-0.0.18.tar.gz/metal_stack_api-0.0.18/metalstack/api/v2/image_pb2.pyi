import datetime

from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from metalstack.api.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageFeature(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMAGE_FEATURE_UNSPECIFIED: _ClassVar[ImageFeature]
    IMAGE_FEATURE_MACHINE: _ClassVar[ImageFeature]
    IMAGE_FEATURE_FIREWALL: _ClassVar[ImageFeature]

class ImageClassification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMAGE_CLASSIFICATION_UNSPECIFIED: _ClassVar[ImageClassification]
    IMAGE_CLASSIFICATION_PREVIEW: _ClassVar[ImageClassification]
    IMAGE_CLASSIFICATION_SUPPORTED: _ClassVar[ImageClassification]
    IMAGE_CLASSIFICATION_DEPRECATED: _ClassVar[ImageClassification]
IMAGE_FEATURE_UNSPECIFIED: ImageFeature
IMAGE_FEATURE_MACHINE: ImageFeature
IMAGE_FEATURE_FIREWALL: ImageFeature
IMAGE_CLASSIFICATION_UNSPECIFIED: ImageClassification
IMAGE_CLASSIFICATION_PREVIEW: ImageClassification
IMAGE_CLASSIFICATION_SUPPORTED: ImageClassification
IMAGE_CLASSIFICATION_DEPRECATED: ImageClassification

class ImageServiceGetRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ImageServiceListRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: ImageQuery
    def __init__(self, query: _Optional[_Union[ImageQuery, _Mapping]] = ...) -> None: ...

class ImageServiceLatestRequest(_message.Message):
    __slots__ = ("os",)
    OS_FIELD_NUMBER: _ClassVar[int]
    os: str
    def __init__(self, os: _Optional[str] = ...) -> None: ...

class ImageServiceGetResponse(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: Image
    def __init__(self, image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class ImageServiceListResponse(_message.Message):
    __slots__ = ("images",)
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[Image]
    def __init__(self, images: _Optional[_Iterable[_Union[Image, _Mapping]]] = ...) -> None: ...

class ImageServiceLatestResponse(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: Image
    def __init__(self, image: _Optional[_Union[Image, _Mapping]] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("id", "meta", "url", "name", "description", "features", "classification", "expires_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    meta: _common_pb2.Meta
    url: str
    name: str
    description: str
    features: _containers.RepeatedScalarFieldContainer[ImageFeature]
    classification: ImageClassification
    expires_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., meta: _Optional[_Union[_common_pb2.Meta, _Mapping]] = ..., url: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., features: _Optional[_Iterable[_Union[ImageFeature, str]]] = ..., classification: _Optional[_Union[ImageClassification, str]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ImageUsage(_message.Message):
    __slots__ = ("image", "used_by")
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    USED_BY_FIELD_NUMBER: _ClassVar[int]
    image: Image
    used_by: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, image: _Optional[_Union[Image, _Mapping]] = ..., used_by: _Optional[_Iterable[str]] = ...) -> None: ...

class ImageQuery(_message.Message):
    __slots__ = ("id", "os", "version", "name", "description", "feature", "classification")
    ID_FIELD_NUMBER: _ClassVar[int]
    OS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    os: str
    version: str
    name: str
    description: str
    feature: ImageFeature
    classification: ImageClassification
    def __init__(self, id: _Optional[str] = ..., os: _Optional[str] = ..., version: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., feature: _Optional[_Union[ImageFeature, str]] = ..., classification: _Optional[_Union[ImageClassification, str]] = ...) -> None: ...
