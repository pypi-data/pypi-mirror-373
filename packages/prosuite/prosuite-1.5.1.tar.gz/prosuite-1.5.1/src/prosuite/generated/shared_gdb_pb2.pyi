from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AttributeValue(_message.Message):
    __slots__ = ["blob_value", "date_time_ticks_value", "db_null", "double_value", "float_value", "long_int_value", "short_int_value", "string_value", "uuid_value"]
    BLOB_VALUE_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_TICKS_VALUE_FIELD_NUMBER: _ClassVar[int]
    DB_NULL_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LONG_INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    SHORT_INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    UUID_VALUE_FIELD_NUMBER: _ClassVar[int]
    blob_value: bytes
    date_time_ticks_value: int
    db_null: bool
    double_value: float
    float_value: float
    long_int_value: int
    short_int_value: int
    string_value: str
    uuid_value: UUID
    def __init__(self, db_null: bool = ..., short_int_value: _Optional[int] = ..., long_int_value: _Optional[int] = ..., float_value: _Optional[float] = ..., double_value: _Optional[float] = ..., string_value: _Optional[str] = ..., date_time_ticks_value: _Optional[int] = ..., uuid_value: _Optional[_Union[UUID, _Mapping]] = ..., blob_value: _Optional[bytes] = ...) -> None: ...

class EnvelopeMsg(_message.Message):
    __slots__ = ["x_max", "x_min", "y_max", "y_min"]
    X_MAX_FIELD_NUMBER: _ClassVar[int]
    X_MIN_FIELD_NUMBER: _ClassVar[int]
    Y_MAX_FIELD_NUMBER: _ClassVar[int]
    Y_MIN_FIELD_NUMBER: _ClassVar[int]
    x_max: float
    x_min: float
    y_max: float
    y_min: float
    def __init__(self, x_min: _Optional[float] = ..., y_min: _Optional[float] = ..., x_max: _Optional[float] = ..., y_max: _Optional[float] = ...) -> None: ...

class FieldMsg(_message.Message):
    __slots__ = ["alias_name", "domain_name", "is_editable", "is_nullable", "length", "name", "precision", "scale", "type"]
    ALIAS_NAME_FIELD_NUMBER: _ClassVar[int]
    DOMAIN_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_EDITABLE_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    SCALE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    alias_name: str
    domain_name: str
    is_editable: bool
    is_nullable: bool
    length: int
    name: str
    precision: int
    scale: int
    type: int
    def __init__(self, name: _Optional[str] = ..., alias_name: _Optional[str] = ..., type: _Optional[int] = ..., length: _Optional[int] = ..., domain_name: _Optional[str] = ..., scale: _Optional[int] = ..., precision: _Optional[int] = ..., is_nullable: bool = ..., is_editable: bool = ...) -> None: ...

class GdbObjRefMsg(_message.Message):
    __slots__ = ["class_handle", "object_id"]
    CLASS_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    class_handle: int
    object_id: int
    def __init__(self, class_handle: _Optional[int] = ..., object_id: _Optional[int] = ...) -> None: ...

class GdbObjectMsg(_message.Message):
    __slots__ = ["Shape", "class_handle", "object_id", "values"]
    CLASS_HANDLE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    Shape: ShapeMsg
    VALUES_FIELD_NUMBER: _ClassVar[int]
    class_handle: int
    object_id: int
    values: _containers.RepeatedCompositeFieldContainer[AttributeValue]
    def __init__(self, object_id: _Optional[int] = ..., class_handle: _Optional[int] = ..., values: _Optional[_Iterable[_Union[AttributeValue, _Mapping]]] = ..., Shape: _Optional[_Union[ShapeMsg, _Mapping]] = ...) -> None: ...

class InsertedObjectMsg(_message.Message):
    __slots__ = ["inserted_object", "original_reference"]
    INSERTED_OBJECT_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    inserted_object: GdbObjectMsg
    original_reference: GdbObjRefMsg
    def __init__(self, inserted_object: _Optional[_Union[GdbObjectMsg, _Mapping]] = ..., original_reference: _Optional[_Union[GdbObjRefMsg, _Mapping]] = ...) -> None: ...

class KeyValuePairMsg(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class ObjectClassMsg(_message.Message):
    __slots__ = ["alias", "class_handle", "fields", "geometry_type", "name", "spatial_reference", "workspace_handle"]
    ALIAS_FIELD_NUMBER: _ClassVar[int]
    CLASS_HANDLE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    alias: str
    class_handle: int
    fields: _containers.RepeatedCompositeFieldContainer[FieldMsg]
    geometry_type: int
    name: str
    spatial_reference: SpatialReferenceMsg
    workspace_handle: int
    def __init__(self, class_handle: _Optional[int] = ..., workspace_handle: _Optional[int] = ..., name: _Optional[str] = ..., alias: _Optional[str] = ..., geometry_type: _Optional[int] = ..., spatial_reference: _Optional[_Union[SpatialReferenceMsg, _Mapping]] = ..., fields: _Optional[_Iterable[_Union[FieldMsg, _Mapping]]] = ...) -> None: ...

class ResultObjectMsg(_message.Message):
    __slots__ = ["delete", "has_warning", "insert", "notifications", "update"]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    HAS_WARNING_FIELD_NUMBER: _ClassVar[int]
    INSERT_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    delete: GdbObjRefMsg
    has_warning: bool
    insert: InsertedObjectMsg
    notifications: _containers.RepeatedScalarFieldContainer[str]
    update: GdbObjectMsg
    def __init__(self, update: _Optional[_Union[GdbObjectMsg, _Mapping]] = ..., insert: _Optional[_Union[InsertedObjectMsg, _Mapping]] = ..., delete: _Optional[_Union[GdbObjRefMsg, _Mapping]] = ..., notifications: _Optional[_Iterable[str]] = ..., has_warning: bool = ...) -> None: ...

class ShapeMsg(_message.Message):
    __slots__ = ["envelope", "esri_shape", "spatial_reference", "wkb"]
    ENVELOPE_FIELD_NUMBER: _ClassVar[int]
    ESRI_SHAPE_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    WKB_FIELD_NUMBER: _ClassVar[int]
    envelope: EnvelopeMsg
    esri_shape: bytes
    spatial_reference: SpatialReferenceMsg
    wkb: bytes
    def __init__(self, esri_shape: _Optional[bytes] = ..., wkb: _Optional[bytes] = ..., envelope: _Optional[_Union[EnvelopeMsg, _Mapping]] = ..., spatial_reference: _Optional[_Union[SpatialReferenceMsg, _Mapping]] = ...) -> None: ...

class SpatialReferenceMsg(_message.Message):
    __slots__ = ["spatial_reference_esri_xml", "spatial_reference_wkid", "spatial_reference_wkt"]
    SPATIAL_REFERENCE_ESRI_XML_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_REFERENCE_WKID_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_REFERENCE_WKT_FIELD_NUMBER: _ClassVar[int]
    spatial_reference_esri_xml: str
    spatial_reference_wkid: int
    spatial_reference_wkt: str
    def __init__(self, spatial_reference_esri_xml: _Optional[str] = ..., spatial_reference_wkt: _Optional[str] = ..., spatial_reference_wkid: _Optional[int] = ...) -> None: ...

class UUID(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class WorkspaceMsg(_message.Message):
    __slots__ = ["connection_properties", "default_version_creation_ticks", "default_version_description", "default_version_modification_ticks", "default_version_name", "path", "version_name", "workspace_db_type", "workspace_handle"]
    CONNECTION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERSION_CREATION_TICKS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERSION_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERSION_MODIFICATION_TICKS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VERSION_NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    VERSION_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_DB_TYPE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    connection_properties: _containers.RepeatedCompositeFieldContainer[KeyValuePairMsg]
    default_version_creation_ticks: int
    default_version_description: str
    default_version_modification_ticks: int
    default_version_name: str
    path: str
    version_name: str
    workspace_db_type: int
    workspace_handle: int
    def __init__(self, workspace_handle: _Optional[int] = ..., workspace_db_type: _Optional[int] = ..., path: _Optional[str] = ..., version_name: _Optional[str] = ..., default_version_name: _Optional[str] = ..., default_version_description: _Optional[str] = ..., default_version_creation_ticks: _Optional[int] = ..., connection_properties: _Optional[_Iterable[_Union[KeyValuePairMsg, _Mapping]]] = ..., default_version_modification_ticks: _Optional[int] = ...) -> None: ...
