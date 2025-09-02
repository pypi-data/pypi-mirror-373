import shared_gdb_pb2 as _shared_gdb_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssociationMsg(_message.Message):
    __slots__ = ["association_id", "association_type", "attributes", "cardinality", "end1_cascade_delete_orphans", "end1_cascade_deletion", "end1_copy_policy", "end1_dataset", "end1_document_edit", "end1_id", "end1_name", "end2_cascade_delete_orphans", "end2_cascade_deletion", "end2_copy_policy", "end2_dataset", "end2_document_edit", "end2_id", "end2_name", "model_id", "name"]
    ASSOCIATION_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    END1_CASCADE_DELETE_ORPHANS_FIELD_NUMBER: _ClassVar[int]
    END1_CASCADE_DELETION_FIELD_NUMBER: _ClassVar[int]
    END1_COPY_POLICY_FIELD_NUMBER: _ClassVar[int]
    END1_DATASET_FIELD_NUMBER: _ClassVar[int]
    END1_DOCUMENT_EDIT_FIELD_NUMBER: _ClassVar[int]
    END1_ID_FIELD_NUMBER: _ClassVar[int]
    END1_NAME_FIELD_NUMBER: _ClassVar[int]
    END2_CASCADE_DELETE_ORPHANS_FIELD_NUMBER: _ClassVar[int]
    END2_CASCADE_DELETION_FIELD_NUMBER: _ClassVar[int]
    END2_COPY_POLICY_FIELD_NUMBER: _ClassVar[int]
    END2_DATASET_FIELD_NUMBER: _ClassVar[int]
    END2_DOCUMENT_EDIT_FIELD_NUMBER: _ClassVar[int]
    END2_ID_FIELD_NUMBER: _ClassVar[int]
    END2_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    association_id: int
    association_type: int
    attributes: _containers.RepeatedCompositeFieldContainer[AttributeMsg]
    cardinality: int
    end1_cascade_delete_orphans: bool
    end1_cascade_deletion: bool
    end1_copy_policy: int
    end1_dataset: int
    end1_document_edit: bool
    end1_id: int
    end1_name: str
    end2_cascade_delete_orphans: bool
    end2_cascade_deletion: bool
    end2_copy_policy: int
    end2_dataset: int
    end2_document_edit: bool
    end2_id: int
    end2_name: str
    model_id: int
    name: str
    def __init__(self, association_id: _Optional[int] = ..., name: _Optional[str] = ..., association_type: _Optional[int] = ..., cardinality: _Optional[int] = ..., end1_dataset: _Optional[int] = ..., end2_dataset: _Optional[int] = ..., end1_id: _Optional[int] = ..., end2_id: _Optional[int] = ..., end1_name: _Optional[str] = ..., end2_name: _Optional[str] = ..., end1_document_edit: bool = ..., end2_document_edit: bool = ..., end1_cascade_deletion: bool = ..., end2_cascade_deletion: bool = ..., end1_cascade_delete_orphans: bool = ..., end2_cascade_delete_orphans: bool = ..., end1_copy_policy: _Optional[int] = ..., end2_copy_policy: _Optional[int] = ..., attributes: _Optional[_Iterable[_Union[AttributeMsg, _Mapping]]] = ..., model_id: _Optional[int] = ...) -> None: ...

class AttributeMsg(_message.Message):
    __slots__ = ["attribute_id", "attribute_role", "is_object_defining", "is_readonly", "name", "non_applicable_value", "type"]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_OBJECT_DEFINING_FIELD_NUMBER: _ClassVar[int]
    IS_READONLY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NON_APPLICABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    attribute_id: int
    attribute_role: int
    is_object_defining: bool
    is_readonly: bool
    name: str
    non_applicable_value: _shared_gdb_pb2.AttributeValue
    type: int
    def __init__(self, attribute_id: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[int] = ..., is_readonly: bool = ..., is_object_defining: bool = ..., attribute_role: _Optional[int] = ..., non_applicable_value: _Optional[_Union[_shared_gdb_pb2.AttributeValue, _Mapping]] = ...) -> None: ...

class ConnectionMsg(_message.Message):
    __slots__ = ["connection_id", "connection_string", "connection_type", "name"]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_STRING_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    connection_id: int
    connection_string: str
    connection_type: int
    name: str
    def __init__(self, connection_id: _Optional[int] = ..., name: _Optional[str] = ..., connection_type: _Optional[int] = ..., connection_string: _Optional[str] = ...) -> None: ...

class DatasetMsg(_message.Message):
    __slots__ = ["alias_name", "attributes", "dataset_id", "dataset_type", "default_symbology", "geometry_type", "model_id", "name", "object_categories", "type_code"]
    ALIAS_NAME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_SYMBOLOGY_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    TYPE_CODE_FIELD_NUMBER: _ClassVar[int]
    alias_name: str
    attributes: _containers.RepeatedCompositeFieldContainer[AttributeMsg]
    dataset_id: int
    dataset_type: int
    default_symbology: str
    geometry_type: int
    model_id: int
    name: str
    object_categories: _containers.RepeatedCompositeFieldContainer[ObjectCategoryMsg]
    type_code: int
    def __init__(self, dataset_id: _Optional[int] = ..., name: _Optional[str] = ..., alias_name: _Optional[str] = ..., geometry_type: _Optional[int] = ..., dataset_type: _Optional[int] = ..., default_symbology: _Optional[str] = ..., attributes: _Optional[_Iterable[_Union[AttributeMsg, _Mapping]]] = ..., object_categories: _Optional[_Iterable[_Union[ObjectCategoryMsg, _Mapping]]] = ..., type_code: _Optional[int] = ..., model_id: _Optional[int] = ...) -> None: ...

class LinearNetworkMsg(_message.Message):
    __slots__ = ["custom_tolerance", "description", "enforce_flow_direction", "linear_network_id", "name", "network_datasets"]
    CUSTOM_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ENFORCE_FLOW_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LINEAR_NETWORK_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NETWORK_DATASETS_FIELD_NUMBER: _ClassVar[int]
    custom_tolerance: float
    description: str
    enforce_flow_direction: bool
    linear_network_id: int
    name: str
    network_datasets: _containers.RepeatedCompositeFieldContainer[NetworkDatasetMsg]
    def __init__(self, linear_network_id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., custom_tolerance: _Optional[float] = ..., enforce_flow_direction: bool = ..., network_datasets: _Optional[_Iterable[_Union[NetworkDatasetMsg, _Mapping]]] = ...) -> None: ...

class ModelMsg(_message.Message):
    __slots__ = ["dataset_ids", "default_database_name", "default_database_schema_owner", "element_names_are_qualified", "error_dataset_ids", "master_db_workspace_handle", "model_id", "name", "spatial_reference", "sql_case_sensitivity", "use_default_database_only_for_schema", "user_connection"]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_DATABASE_NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_DATABASE_SCHEMA_OWNER_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_NAMES_ARE_QUALIFIED_FIELD_NUMBER: _ClassVar[int]
    ERROR_DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    MASTER_DB_WORKSPACE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SPATIAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    SQL_CASE_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    USER_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    USE_DEFAULT_DATABASE_ONLY_FOR_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    dataset_ids: _containers.RepeatedScalarFieldContainer[int]
    default_database_name: str
    default_database_schema_owner: str
    element_names_are_qualified: bool
    error_dataset_ids: _containers.RepeatedScalarFieldContainer[int]
    master_db_workspace_handle: int
    model_id: int
    name: str
    spatial_reference: _shared_gdb_pb2.SpatialReferenceMsg
    sql_case_sensitivity: int
    use_default_database_only_for_schema: bool
    user_connection: ConnectionMsg
    def __init__(self, model_id: _Optional[int] = ..., name: _Optional[str] = ..., spatial_reference: _Optional[_Union[_shared_gdb_pb2.SpatialReferenceMsg, _Mapping]] = ..., dataset_ids: _Optional[_Iterable[int]] = ..., error_dataset_ids: _Optional[_Iterable[int]] = ..., master_db_workspace_handle: _Optional[int] = ..., element_names_are_qualified: bool = ..., default_database_name: _Optional[str] = ..., default_database_schema_owner: _Optional[str] = ..., sql_case_sensitivity: _Optional[int] = ..., user_connection: _Optional[_Union[ConnectionMsg, _Mapping]] = ..., use_default_database_only_for_schema: bool = ...) -> None: ...

class NetworkDatasetMsg(_message.Message):
    __slots__ = ["dataset_id", "is_default_junction", "is_splitting", "where_clause"]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_JUNCTION_FIELD_NUMBER: _ClassVar[int]
    IS_SPLITTING_FIELD_NUMBER: _ClassVar[int]
    WHERE_CLAUSE_FIELD_NUMBER: _ClassVar[int]
    dataset_id: int
    is_default_junction: bool
    is_splitting: bool
    where_clause: str
    def __init__(self, dataset_id: _Optional[int] = ..., where_clause: _Optional[str] = ..., is_default_junction: bool = ..., is_splitting: bool = ...) -> None: ...

class ObjectCategoryAttributeConstraintMsg(_message.Message):
    __slots__ = ["attribute_id", "dataset_id", "object_category_id"]
    ATTRIBUTE_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    attribute_id: int
    dataset_id: int
    object_category_id: int
    def __init__(self, dataset_id: _Optional[int] = ..., object_category_id: _Optional[int] = ..., attribute_id: _Optional[int] = ...) -> None: ...

class ObjectCategoryMsg(_message.Message):
    __slots__ = ["name", "object_category_id", "object_subtype_criterion", "subtype_code"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_SUBTYPE_CRITERION_FIELD_NUMBER: _ClassVar[int]
    SUBTYPE_CODE_FIELD_NUMBER: _ClassVar[int]
    name: str
    object_category_id: int
    object_subtype_criterion: _containers.RepeatedCompositeFieldContainer[ObjectSubtypeCriterionMsg]
    subtype_code: int
    def __init__(self, object_category_id: _Optional[int] = ..., name: _Optional[str] = ..., subtype_code: _Optional[int] = ..., object_subtype_criterion: _Optional[_Iterable[_Union[ObjectSubtypeCriterionMsg, _Mapping]]] = ...) -> None: ...

class ObjectSubtypeCriterionMsg(_message.Message):
    __slots__ = ["attribute_name", "attribute_value"]
    ATTRIBUTE_NAME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTE_VALUE_FIELD_NUMBER: _ClassVar[int]
    attribute_name: str
    attribute_value: _shared_gdb_pb2.AttributeValue
    def __init__(self, attribute_name: _Optional[str] = ..., attribute_value: _Optional[_Union[_shared_gdb_pb2.AttributeValue, _Mapping]] = ...) -> None: ...

class ProjectMsg(_message.Message):
    __slots__ = ["attribute_editor_config_dir", "description", "exclude_read_only_datasets_from_project_workspace", "full_extent_x_max", "full_extent_x_min", "full_extent_y_max", "full_extent_y_min", "minimum_scale_denominator", "model_id", "name", "project_id", "short_name", "tool_config_directory", "work_list_config_dir"]
    ATTRIBUTE_EDITOR_CONFIG_DIR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_READ_ONLY_DATASETS_FROM_PROJECT_WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FULL_EXTENT_X_MAX_FIELD_NUMBER: _ClassVar[int]
    FULL_EXTENT_X_MIN_FIELD_NUMBER: _ClassVar[int]
    FULL_EXTENT_Y_MAX_FIELD_NUMBER: _ClassVar[int]
    FULL_EXTENT_Y_MIN_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_SCALE_DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CONFIG_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    WORK_LIST_CONFIG_DIR_FIELD_NUMBER: _ClassVar[int]
    attribute_editor_config_dir: str
    description: str
    exclude_read_only_datasets_from_project_workspace: bool
    full_extent_x_max: float
    full_extent_x_min: float
    full_extent_y_max: float
    full_extent_y_min: float
    minimum_scale_denominator: float
    model_id: int
    name: str
    project_id: int
    short_name: str
    tool_config_directory: str
    work_list_config_dir: str
    def __init__(self, project_id: _Optional[int] = ..., model_id: _Optional[int] = ..., name: _Optional[str] = ..., short_name: _Optional[str] = ..., minimum_scale_denominator: _Optional[float] = ..., tool_config_directory: _Optional[str] = ..., attribute_editor_config_dir: _Optional[str] = ..., work_list_config_dir: _Optional[str] = ..., description: _Optional[str] = ..., exclude_read_only_datasets_from_project_workspace: bool = ..., full_extent_x_min: _Optional[float] = ..., full_extent_y_min: _Optional[float] = ..., full_extent_x_max: _Optional[float] = ..., full_extent_y_max: _Optional[float] = ...) -> None: ...
