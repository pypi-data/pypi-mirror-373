import shared_gdb_pb2 as _shared_gdb_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClassDef(_message.Message):
    __slots__ = ["class_handle", "workspace_handle"]
    CLASS_HANDLE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    class_handle: int
    workspace_handle: int
    def __init__(self, class_handle: _Optional[int] = ..., workspace_handle: _Optional[int] = ...) -> None: ...

class ClassDescriptorMsg(_message.Message):
    __slots__ = ["assembly_name", "type_name"]
    ASSEMBLY_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    assembly_name: str
    type_name: str
    def __init__(self, type_name: _Optional[str] = ..., assembly_name: _Optional[str] = ...) -> None: ...

class ConditionListSpecificationMsg(_message.Message):
    __slots__ = ["data_sources", "description", "elements", "name"]
    DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    data_sources: _containers.RepeatedCompositeFieldContainer[DataSourceMsg]
    description: str
    elements: _containers.RepeatedCompositeFieldContainer[QualitySpecificationElementMsg]
    name: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., elements: _Optional[_Iterable[_Union[QualitySpecificationElementMsg, _Mapping]]] = ..., data_sources: _Optional[_Iterable[_Union[DataSourceMsg, _Mapping]]] = ...) -> None: ...

class DataRequest(_message.Message):
    __slots__ = ["class_def", "count_only", "rel_query_def", "search_geometry", "sub_fields", "where_clause"]
    CLASS_DEF_FIELD_NUMBER: _ClassVar[int]
    COUNT_ONLY_FIELD_NUMBER: _ClassVar[int]
    REL_QUERY_DEF_FIELD_NUMBER: _ClassVar[int]
    SEARCH_GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    SUB_FIELDS_FIELD_NUMBER: _ClassVar[int]
    WHERE_CLAUSE_FIELD_NUMBER: _ClassVar[int]
    class_def: ClassDef
    count_only: bool
    rel_query_def: RelationshipClassQuery
    search_geometry: _shared_gdb_pb2.ShapeMsg
    sub_fields: str
    where_clause: str
    def __init__(self, class_def: _Optional[_Union[ClassDef, _Mapping]] = ..., rel_query_def: _Optional[_Union[RelationshipClassQuery, _Mapping]] = ..., where_clause: _Optional[str] = ..., search_geometry: _Optional[_Union[_shared_gdb_pb2.ShapeMsg, _Mapping]] = ..., sub_fields: _Optional[str] = ..., count_only: bool = ...) -> None: ...

class DataSourceMsg(_message.Message):
    __slots__ = ["catalog_path", "database", "id", "model_name", "schema_owner"]
    CATALOG_PATH_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_OWNER_FIELD_NUMBER: _ClassVar[int]
    catalog_path: str
    database: str
    id: str
    model_name: str
    schema_owner: str
    def __init__(self, id: _Optional[str] = ..., catalog_path: _Optional[str] = ..., model_name: _Optional[str] = ..., database: _Optional[str] = ..., schema_owner: _Optional[str] = ...) -> None: ...

class GdbData(_message.Message):
    __slots__ = ["gdb_object_count", "gdb_objects"]
    GDB_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    GDB_OBJECT_COUNT_FIELD_NUMBER: _ClassVar[int]
    gdb_object_count: int
    gdb_objects: _containers.RepeatedCompositeFieldContainer[_shared_gdb_pb2.GdbObjectMsg]
    def __init__(self, gdb_object_count: _Optional[int] = ..., gdb_objects: _Optional[_Iterable[_Union[_shared_gdb_pb2.GdbObjectMsg, _Mapping]]] = ...) -> None: ...

class InstanceConfigurationMsg(_message.Message):
    __slots__ = ["description", "id", "instance_descriptor_name", "name", "parameters", "url"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_DESCRIPTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    description: str
    id: int
    instance_descriptor_name: str
    name: str
    parameters: _containers.RepeatedCompositeFieldContainer[ParameterMsg]
    url: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., instance_descriptor_name: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[ParameterMsg, _Mapping]]] = ...) -> None: ...

class InstanceDescriptorMsg(_message.Message):
    __slots__ = ["class_descriptor", "constructor", "description", "id", "name", "type"]
    CLASS_DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    CONSTRUCTOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    class_descriptor: ClassDescriptorMsg
    constructor: int
    description: str
    id: int
    name: str
    type: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[int] = ..., class_descriptor: _Optional[_Union[ClassDescriptorMsg, _Mapping]] = ..., constructor: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class InvolvedTableMsg(_message.Message):
    __slots__ = ["object_ids", "table_name"]
    OBJECT_IDS_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    object_ids: _containers.RepeatedScalarFieldContainer[int]
    table_name: str
    def __init__(self, table_name: _Optional[str] = ..., object_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class IssueMsg(_message.Message):
    __slots__ = ["affected_component", "allowable", "condition_id", "creation_date_time_ticks", "description", "involved_tables", "issue_code_description", "issue_code_id", "issue_geometry", "legacy_involved_rows", "stop_condition", "test"]
    AFFECTED_COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ALLOWABLE_FIELD_NUMBER: _ClassVar[int]
    CONDITION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_TIME_TICKS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INVOLVED_TABLES_FIELD_NUMBER: _ClassVar[int]
    ISSUE_CODE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ISSUE_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    ISSUE_GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    LEGACY_INVOLVED_ROWS_FIELD_NUMBER: _ClassVar[int]
    STOP_CONDITION_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    affected_component: str
    allowable: bool
    condition_id: int
    creation_date_time_ticks: int
    description: str
    involved_tables: _containers.RepeatedCompositeFieldContainer[InvolvedTableMsg]
    issue_code_description: str
    issue_code_id: str
    issue_geometry: _shared_gdb_pb2.ShapeMsg
    legacy_involved_rows: str
    stop_condition: bool
    test: int
    def __init__(self, condition_id: _Optional[int] = ..., issue_geometry: _Optional[_Union[_shared_gdb_pb2.ShapeMsg, _Mapping]] = ..., description: _Optional[str] = ..., issue_code_id: _Optional[str] = ..., issue_code_description: _Optional[str] = ..., involved_tables: _Optional[_Iterable[_Union[InvolvedTableMsg, _Mapping]]] = ..., legacy_involved_rows: _Optional[str] = ..., allowable: bool = ..., stop_condition: bool = ..., affected_component: _Optional[str] = ..., creation_date_time_ticks: _Optional[int] = ..., test: _Optional[int] = ...) -> None: ...

class LogMsg(_message.Message):
    __slots__ = ["message", "message_level"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    message: str
    message_level: int
    def __init__(self, message: _Optional[str] = ..., message_level: _Optional[int] = ...) -> None: ...

class ParameterMsg(_message.Message):
    __slots__ = ["name", "transformer", "used_as_reference_data", "value", "where_clause", "workspace_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMER_FIELD_NUMBER: _ClassVar[int]
    USED_AS_REFERENCE_DATA_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WHERE_CLAUSE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    transformer: InstanceConfigurationMsg
    used_as_reference_data: bool
    value: str
    where_clause: str
    workspace_id: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ..., transformer: _Optional[_Union[InstanceConfigurationMsg, _Mapping]] = ..., where_clause: _Optional[str] = ..., workspace_id: _Optional[str] = ..., used_as_reference_data: bool = ...) -> None: ...

class QualityConditionMsg(_message.Message):
    __slots__ = ["condition_id", "condition_issue_filters", "description", "issue_filter_expression", "name", "parameters", "test_descriptor_name", "url"]
    CONDITION_ID_FIELD_NUMBER: _ClassVar[int]
    CONDITION_ISSUE_FILTERS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ISSUE_FILTER_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TEST_DESCRIPTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    condition_id: int
    condition_issue_filters: _containers.RepeatedCompositeFieldContainer[InstanceConfigurationMsg]
    description: str
    issue_filter_expression: str
    name: str
    parameters: _containers.RepeatedCompositeFieldContainer[ParameterMsg]
    test_descriptor_name: str
    url: str
    def __init__(self, condition_id: _Optional[int] = ..., name: _Optional[str] = ..., test_descriptor_name: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[ParameterMsg, _Mapping]]] = ..., condition_issue_filters: _Optional[_Iterable[_Union[InstanceConfigurationMsg, _Mapping]]] = ..., issue_filter_expression: _Optional[str] = ...) -> None: ...

class QualityConditionVerificationMsg(_message.Message):
    __slots__ = ["error_count", "execute_time", "fulfilled", "quality_condition_id", "row_execute_time", "stop_condition_id", "tile_execute_time"]
    ERROR_COUNT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_TIME_FIELD_NUMBER: _ClassVar[int]
    FULFILLED_FIELD_NUMBER: _ClassVar[int]
    QUALITY_CONDITION_ID_FIELD_NUMBER: _ClassVar[int]
    ROW_EXECUTE_TIME_FIELD_NUMBER: _ClassVar[int]
    STOP_CONDITION_ID_FIELD_NUMBER: _ClassVar[int]
    TILE_EXECUTE_TIME_FIELD_NUMBER: _ClassVar[int]
    error_count: int
    execute_time: float
    fulfilled: bool
    quality_condition_id: int
    row_execute_time: float
    stop_condition_id: int
    tile_execute_time: float
    def __init__(self, quality_condition_id: _Optional[int] = ..., stop_condition_id: _Optional[int] = ..., fulfilled: bool = ..., error_count: _Optional[int] = ..., execute_time: _Optional[float] = ..., row_execute_time: _Optional[float] = ..., tile_execute_time: _Optional[float] = ...) -> None: ...

class QualitySpecificationElementMsg(_message.Message):
    __slots__ = ["allow_errors", "category_name", "condition", "stop_on_error"]
    ALLOW_ERRORS_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_NAME_FIELD_NUMBER: _ClassVar[int]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    STOP_ON_ERROR_FIELD_NUMBER: _ClassVar[int]
    allow_errors: bool
    category_name: str
    condition: QualityConditionMsg
    stop_on_error: bool
    def __init__(self, condition: _Optional[_Union[QualityConditionMsg, _Mapping]] = ..., allow_errors: bool = ..., stop_on_error: bool = ..., category_name: _Optional[str] = ...) -> None: ...

class QualitySpecificationMsg(_message.Message):
    __slots__ = ["condition_list_specification", "excluded_condition_ids", "quality_specification_id", "well_known_specification", "xml_specification"]
    CONDITION_LIST_SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_CONDITION_IDS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SPECIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    WELL_KNOWN_SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    XML_SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    condition_list_specification: ConditionListSpecificationMsg
    excluded_condition_ids: _containers.RepeatedScalarFieldContainer[int]
    quality_specification_id: int
    well_known_specification: int
    xml_specification: XmlQualitySpecificationMsg
    def __init__(self, quality_specification_id: _Optional[int] = ..., well_known_specification: _Optional[int] = ..., xml_specification: _Optional[_Union[XmlQualitySpecificationMsg, _Mapping]] = ..., condition_list_specification: _Optional[_Union[ConditionListSpecificationMsg, _Mapping]] = ..., excluded_condition_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class QualityVerificationDatasetMsg(_message.Message):
    __slots__ = ["dataset_id", "load_time"]
    DATASET_ID_FIELD_NUMBER: _ClassVar[int]
    LOAD_TIME_FIELD_NUMBER: _ClassVar[int]
    dataset_id: int
    load_time: float
    def __init__(self, dataset_id: _Optional[int] = ..., load_time: _Optional[float] = ...) -> None: ...

class QualityVerificationMsg(_message.Message):
    __slots__ = ["cancelled", "condition_verifications", "context_name", "context_type", "end_time_ticks", "fulfilled", "processor_time_seconds", "rows_with_stop_conditions", "saved_verification_id", "specification_description", "specification_id", "specification_name", "start_time_ticks", "user_name", "verification_datasets"]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    CONDITION_VERIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_TYPE_FIELD_NUMBER: _ClassVar[int]
    END_TIME_TICKS_FIELD_NUMBER: _ClassVar[int]
    FULFILLED_FIELD_NUMBER: _ClassVar[int]
    PROCESSOR_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ROWS_WITH_STOP_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    SAVED_VERIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATION_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_TICKS_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_DATASETS_FIELD_NUMBER: _ClassVar[int]
    cancelled: bool
    condition_verifications: _containers.RepeatedCompositeFieldContainer[QualityConditionVerificationMsg]
    context_name: str
    context_type: str
    end_time_ticks: int
    fulfilled: bool
    processor_time_seconds: float
    rows_with_stop_conditions: int
    saved_verification_id: int
    specification_description: str
    specification_id: int
    specification_name: str
    start_time_ticks: int
    user_name: str
    verification_datasets: _containers.RepeatedCompositeFieldContainer[QualityVerificationDatasetMsg]
    def __init__(self, saved_verification_id: _Optional[int] = ..., specification_id: _Optional[int] = ..., specification_name: _Optional[str] = ..., specification_description: _Optional[str] = ..., user_name: _Optional[str] = ..., start_time_ticks: _Optional[int] = ..., end_time_ticks: _Optional[int] = ..., fulfilled: bool = ..., cancelled: bool = ..., processor_time_seconds: _Optional[float] = ..., context_type: _Optional[str] = ..., context_name: _Optional[str] = ..., rows_with_stop_conditions: _Optional[int] = ..., condition_verifications: _Optional[_Iterable[_Union[QualityConditionVerificationMsg, _Mapping]]] = ..., verification_datasets: _Optional[_Iterable[_Union[QualityVerificationDatasetMsg, _Mapping]]] = ...) -> None: ...

class RelationshipClassQuery(_message.Message):
    __slots__ = ["join_type", "relationship_class_name", "tables", "where_clause", "workspace_handle"]
    JOIN_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    TABLES_FIELD_NUMBER: _ClassVar[int]
    WHERE_CLAUSE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_HANDLE_FIELD_NUMBER: _ClassVar[int]
    join_type: int
    relationship_class_name: str
    tables: _containers.RepeatedScalarFieldContainer[str]
    where_clause: str
    workspace_handle: int
    def __init__(self, relationship_class_name: _Optional[str] = ..., workspace_handle: _Optional[int] = ..., tables: _Optional[_Iterable[str]] = ..., join_type: _Optional[int] = ..., where_clause: _Optional[str] = ...) -> None: ...

class SchemaMsg(_message.Message):
    __slots__ = ["class_definitions", "relclass_definitions"]
    CLASS_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    RELCLASS_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    class_definitions: _containers.RepeatedCompositeFieldContainer[_shared_gdb_pb2.ObjectClassMsg]
    relclass_definitions: _containers.RepeatedCompositeFieldContainer[_shared_gdb_pb2.ObjectClassMsg]
    def __init__(self, class_definitions: _Optional[_Iterable[_Union[_shared_gdb_pb2.ObjectClassMsg, _Mapping]]] = ..., relclass_definitions: _Optional[_Iterable[_Union[_shared_gdb_pb2.ObjectClassMsg, _Mapping]]] = ...) -> None: ...

class SchemaRequest(_message.Message):
    __slots__ = ["dataset_ids", "relationship_class_queries"]
    DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    RELATIONSHIP_CLASS_QUERIES_FIELD_NUMBER: _ClassVar[int]
    dataset_ids: _containers.RepeatedScalarFieldContainer[int]
    relationship_class_queries: _containers.RepeatedCompositeFieldContainer[RelationshipClassQuery]
    def __init__(self, dataset_ids: _Optional[_Iterable[int]] = ..., relationship_class_queries: _Optional[_Iterable[_Union[RelationshipClassQuery, _Mapping]]] = ...) -> None: ...

class VerificationParametersMsg(_message.Message):
    __slots__ = ["filter_table_rows_using_related_geometry", "force_full_scan_for_non_container_tests", "html_report_path", "html_template_path", "invalidate_exceptions_if_any_involved_object_changed", "invalidate_exceptions_if_condition_was_updated", "issue_file_gdb_path", "issue_repository_spatial_reference", "override_allowed_errors", "perimeter", "report_culture_code", "report_invalid_exceptions", "report_issues_outside_perimeter", "report_unused_exceptions", "save_verification_statistics", "store_related_geometry_for_table_row_issues", "tile_size", "update_issues_in_verified_model", "verification_report_path", "write_detailed_verification_report"]
    FILTER_TABLE_ROWS_USING_RELATED_GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    FORCE_FULL_SCAN_FOR_NON_CONTAINER_TESTS_FIELD_NUMBER: _ClassVar[int]
    HTML_REPORT_PATH_FIELD_NUMBER: _ClassVar[int]
    HTML_TEMPLATE_PATH_FIELD_NUMBER: _ClassVar[int]
    INVALIDATE_EXCEPTIONS_IF_ANY_INVOLVED_OBJECT_CHANGED_FIELD_NUMBER: _ClassVar[int]
    INVALIDATE_EXCEPTIONS_IF_CONDITION_WAS_UPDATED_FIELD_NUMBER: _ClassVar[int]
    ISSUE_FILE_GDB_PATH_FIELD_NUMBER: _ClassVar[int]
    ISSUE_REPOSITORY_SPATIAL_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_ALLOWED_ERRORS_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    REPORT_CULTURE_CODE_FIELD_NUMBER: _ClassVar[int]
    REPORT_INVALID_EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    REPORT_ISSUES_OUTSIDE_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    REPORT_UNUSED_EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    SAVE_VERIFICATION_STATISTICS_FIELD_NUMBER: _ClassVar[int]
    STORE_RELATED_GEOMETRY_FOR_TABLE_ROW_ISSUES_FIELD_NUMBER: _ClassVar[int]
    TILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_ISSUES_IN_VERIFIED_MODEL_FIELD_NUMBER: _ClassVar[int]
    VERIFICATION_REPORT_PATH_FIELD_NUMBER: _ClassVar[int]
    WRITE_DETAILED_VERIFICATION_REPORT_FIELD_NUMBER: _ClassVar[int]
    filter_table_rows_using_related_geometry: bool
    force_full_scan_for_non_container_tests: bool
    html_report_path: str
    html_template_path: str
    invalidate_exceptions_if_any_involved_object_changed: bool
    invalidate_exceptions_if_condition_was_updated: bool
    issue_file_gdb_path: str
    issue_repository_spatial_reference: _shared_gdb_pb2.SpatialReferenceMsg
    override_allowed_errors: bool
    perimeter: _shared_gdb_pb2.ShapeMsg
    report_culture_code: str
    report_invalid_exceptions: bool
    report_issues_outside_perimeter: bool
    report_unused_exceptions: bool
    save_verification_statistics: bool
    store_related_geometry_for_table_row_issues: bool
    tile_size: float
    update_issues_in_verified_model: bool
    verification_report_path: str
    write_detailed_verification_report: bool
    def __init__(self, tile_size: _Optional[float] = ..., perimeter: _Optional[_Union[_shared_gdb_pb2.ShapeMsg, _Mapping]] = ..., write_detailed_verification_report: bool = ..., verification_report_path: _Optional[str] = ..., html_report_path: _Optional[str] = ..., html_template_path: _Optional[str] = ..., issue_file_gdb_path: _Optional[str] = ..., store_related_geometry_for_table_row_issues: bool = ..., filter_table_rows_using_related_geometry: bool = ..., override_allowed_errors: bool = ..., report_issues_outside_perimeter: bool = ..., force_full_scan_for_non_container_tests: bool = ..., save_verification_statistics: bool = ..., report_unused_exceptions: bool = ..., report_invalid_exceptions: bool = ..., invalidate_exceptions_if_any_involved_object_changed: bool = ..., invalidate_exceptions_if_condition_was_updated: bool = ..., issue_repository_spatial_reference: _Optional[_Union[_shared_gdb_pb2.SpatialReferenceMsg, _Mapping]] = ..., update_issues_in_verified_model: bool = ..., report_culture_code: _Optional[str] = ...) -> None: ...

class VerificationProgressMsg(_message.Message):
    __slots__ = ["current_box", "detailed_progress__current_step", "detailed_progress_total_steps", "message", "message_level", "overall_progress_current_step", "overall_progress_total_steps", "processing_step_message", "progress_step", "progress_type", "total_box"]
    CURRENT_BOX_FIELD_NUMBER: _ClassVar[int]
    DETAILED_PROGRESS_TOTAL_STEPS_FIELD_NUMBER: _ClassVar[int]
    DETAILED_PROGRESS__CURRENT_STEP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    OVERALL_PROGRESS_CURRENT_STEP_FIELD_NUMBER: _ClassVar[int]
    OVERALL_PROGRESS_TOTAL_STEPS_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_STEP_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_STEP_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BOX_FIELD_NUMBER: _ClassVar[int]
    current_box: _shared_gdb_pb2.EnvelopeMsg
    detailed_progress__current_step: int
    detailed_progress_total_steps: int
    message: str
    message_level: int
    overall_progress_current_step: int
    overall_progress_total_steps: int
    processing_step_message: str
    progress_step: int
    progress_type: int
    total_box: _shared_gdb_pb2.EnvelopeMsg
    def __init__(self, progress_type: _Optional[int] = ..., progress_step: _Optional[int] = ..., overall_progress_total_steps: _Optional[int] = ..., overall_progress_current_step: _Optional[int] = ..., detailed_progress_total_steps: _Optional[int] = ..., detailed_progress__current_step: _Optional[int] = ..., processing_step_message: _Optional[str] = ..., current_box: _Optional[_Union[_shared_gdb_pb2.EnvelopeMsg, _Mapping]] = ..., total_box: _Optional[_Union[_shared_gdb_pb2.EnvelopeMsg, _Mapping]] = ..., message: _Optional[str] = ..., message_level: _Optional[int] = ...) -> None: ...

class WorkContextMsg(_message.Message):
    __slots__ = ["context_name", "context_type", "ddx_id", "type", "verified_dataset_ids", "version_name", "workspace"]
    CONTEXT_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DDX_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_DATASET_IDS_FIELD_NUMBER: _ClassVar[int]
    VERSION_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    context_name: str
    context_type: str
    ddx_id: int
    type: int
    verified_dataset_ids: _containers.RepeatedScalarFieldContainer[int]
    version_name: str
    workspace: _shared_gdb_pb2.WorkspaceMsg
    def __init__(self, ddx_id: _Optional[int] = ..., type: _Optional[int] = ..., workspace: _Optional[_Union[_shared_gdb_pb2.WorkspaceMsg, _Mapping]] = ..., version_name: _Optional[str] = ..., verified_dataset_ids: _Optional[_Iterable[int]] = ..., context_type: _Optional[str] = ..., context_name: _Optional[str] = ...) -> None: ...

class XmlQualitySpecificationMsg(_message.Message):
    __slots__ = ["data_source_replacements", "selected_specification_name", "xml"]
    DATA_SOURCE_REPLACEMENTS_FIELD_NUMBER: _ClassVar[int]
    SELECTED_SPECIFICATION_NAME_FIELD_NUMBER: _ClassVar[int]
    XML_FIELD_NUMBER: _ClassVar[int]
    data_source_replacements: _containers.RepeatedScalarFieldContainer[str]
    selected_specification_name: str
    xml: str
    def __init__(self, xml: _Optional[str] = ..., selected_specification_name: _Optional[str] = ..., data_source_replacements: _Optional[_Iterable[str]] = ...) -> None: ...
