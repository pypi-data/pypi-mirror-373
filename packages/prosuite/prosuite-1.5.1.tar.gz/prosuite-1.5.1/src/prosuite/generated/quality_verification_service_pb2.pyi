import shared_gdb_pb2 as _shared_gdb_pb2
import shared_qa_pb2 as _shared_qa_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataVerificationRequest(_message.Message):
    __slots__ = ["data", "error_message", "request", "schema"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    data: _shared_qa_pb2.GdbData
    error_message: str
    request: VerificationRequest
    schema: _shared_qa_pb2.SchemaMsg
    def __init__(self, request: _Optional[_Union[VerificationRequest, _Mapping]] = ..., data: _Optional[_Union[_shared_qa_pb2.GdbData, _Mapping]] = ..., schema: _Optional[_Union[_shared_qa_pb2.SchemaMsg, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...

class DataVerificationResponse(_message.Message):
    __slots__ = ["data_request", "response", "schema_request"]
    DATA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_REQUEST_FIELD_NUMBER: _ClassVar[int]
    data_request: _shared_qa_pb2.DataRequest
    response: VerificationResponse
    schema_request: _shared_qa_pb2.SchemaRequest
    def __init__(self, response: _Optional[_Union[VerificationResponse, _Mapping]] = ..., data_request: _Optional[_Union[_shared_qa_pb2.DataRequest, _Mapping]] = ..., schema_request: _Optional[_Union[_shared_qa_pb2.SchemaRequest, _Mapping]] = ...) -> None: ...

class StandaloneVerificationRequest(_message.Message):
    __slots__ = ["condition_list_specification", "output_directory", "parameters", "user_name", "xml_specification"]
    CONDITION_LIST_SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    XML_SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    condition_list_specification: _shared_qa_pb2.ConditionListSpecificationMsg
    output_directory: str
    parameters: _shared_qa_pb2.VerificationParametersMsg
    user_name: str
    xml_specification: _shared_qa_pb2.XmlQualitySpecificationMsg
    def __init__(self, xml_specification: _Optional[_Union[_shared_qa_pb2.XmlQualitySpecificationMsg, _Mapping]] = ..., condition_list_specification: _Optional[_Union[_shared_qa_pb2.ConditionListSpecificationMsg, _Mapping]] = ..., parameters: _Optional[_Union[_shared_qa_pb2.VerificationParametersMsg, _Mapping]] = ..., output_directory: _Optional[str] = ..., user_name: _Optional[str] = ...) -> None: ...

class StandaloneVerificationResponse(_message.Message):
    __slots__ = ["issues", "message", "service_call_status"]
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CALL_STATUS_FIELD_NUMBER: _ClassVar[int]
    issues: _containers.RepeatedCompositeFieldContainer[_shared_qa_pb2.IssueMsg]
    message: _shared_qa_pb2.LogMsg
    service_call_status: int
    def __init__(self, service_call_status: _Optional[int] = ..., message: _Optional[_Union[_shared_qa_pb2.LogMsg, _Mapping]] = ..., issues: _Optional[_Iterable[_Union[_shared_qa_pb2.IssueMsg, _Mapping]]] = ...) -> None: ...

class VerificationRequest(_message.Message):
    __slots__ = ["environment", "features", "max_parallel_processing", "parameters", "specification", "user_name", "work_context"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    MAX_PARALLEL_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATION_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    environment: str
    features: _containers.RepeatedCompositeFieldContainer[_shared_gdb_pb2.GdbObjectMsg]
    max_parallel_processing: int
    parameters: _shared_qa_pb2.VerificationParametersMsg
    specification: _shared_qa_pb2.QualitySpecificationMsg
    user_name: str
    work_context: _shared_qa_pb2.WorkContextMsg
    def __init__(self, work_context: _Optional[_Union[_shared_qa_pb2.WorkContextMsg, _Mapping]] = ..., specification: _Optional[_Union[_shared_qa_pb2.QualitySpecificationMsg, _Mapping]] = ..., parameters: _Optional[_Union[_shared_qa_pb2.VerificationParametersMsg, _Mapping]] = ..., features: _Optional[_Iterable[_Union[_shared_gdb_pb2.GdbObjectMsg, _Mapping]]] = ..., user_name: _Optional[str] = ..., max_parallel_processing: _Optional[int] = ..., environment: _Optional[str] = ...) -> None: ...

class VerificationResponse(_message.Message):
    __slots__ = ["issues", "obsolete_exceptions", "progress", "quality_verification", "service_call_status", "verified_perimeter"]
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    OBSOLETE_EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    SERVICE_CALL_STATUS_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    issues: _containers.RepeatedCompositeFieldContainer[_shared_qa_pb2.IssueMsg]
    obsolete_exceptions: _containers.RepeatedCompositeFieldContainer[_shared_gdb_pb2.GdbObjRefMsg]
    progress: _shared_qa_pb2.VerificationProgressMsg
    quality_verification: _shared_qa_pb2.QualityVerificationMsg
    service_call_status: int
    verified_perimeter: _shared_gdb_pb2.ShapeMsg
    def __init__(self, service_call_status: _Optional[int] = ..., progress: _Optional[_Union[_shared_qa_pb2.VerificationProgressMsg, _Mapping]] = ..., issues: _Optional[_Iterable[_Union[_shared_qa_pb2.IssueMsg, _Mapping]]] = ..., quality_verification: _Optional[_Union[_shared_qa_pb2.QualityVerificationMsg, _Mapping]] = ..., verified_perimeter: _Optional[_Union[_shared_gdb_pb2.ShapeMsg, _Mapping]] = ..., obsolete_exceptions: _Optional[_Iterable[_Union[_shared_gdb_pb2.GdbObjRefMsg, _Mapping]]] = ...) -> None: ...
