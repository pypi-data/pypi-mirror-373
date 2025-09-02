import logging
import os
from typing import Union, Iterable, Optional

import grpc

from prosuite.data_model import TransformedDataset
from prosuite.quality import Condition, IssueType, Parameter, Specification, XmlSpecification, DdxSpecification
from prosuite.verification import EnvelopePerimeter, EsriShapePerimeter, WkbPerimeter, VerificationParameters, \
    VerificationResponse, VerifiedCondition, VerifiedSpecification
from prosuite.verification.advanced_parameters import AdvancedParameters
import prosuite.generated.quality_verification_service_pb2 as service_util
import prosuite.generated.quality_verification_service_pb2_grpc as qa_service
import prosuite.generated.shared_qa_pb2 as shared_qa
import prosuite.generated.shared_gdb_pb2 as shared_gdb
from prosuite.verification.message_level import MessageLevel
from prosuite.generated.process_admin_pb2 import CancelRequest
from prosuite.generated.process_admin_pb2_grpc import ProcessAdministrationGrpcStub

MAX_MESSAGE_LENGTH_MB = 1024


class Service:
    """
    The service class communicates on the http/2 channel with the server and initiates the
    quality verifications.
    """

    ISSUE_GDB = "Issues.gdb"
    """
    The name of the issue File Geodatabase. 
    It will be written to the output_dir specified in the :py:meth:`prosuite.service.Service.verify` 
    method. This File Geodatabase contains the issues found during the verification and could 
    be used as the source for the Issue Worklist in the ProSuite QA Add-In for ArcGIS Pro.
    """

    XML_REPORT = "verification.xml"
    """
    The name of the xml verification report.
    It will be written to the output_dir specified in the :py:meth:`prosuite.service.Service.verify` 
    method.
    """

    HTML_REPORT = "verification.html"
    """
    The name of the html verification report.
    It will be written to the output_dir specified in the :py:meth:`prosuite.service.Service.verify` 
    method.
    """

    def __init__(self, host_name: str, port_nr: int, channel_credentials: grpc.ssl_channel_credentials = None):
        #:
        self.host_name = host_name
        """
        The name or IP address of the host running the quality verification service.
        """
        #:
        self.port_nr = port_nr
        """
        The port used by the quality verification service.
        """
        #:
        self.ssl_channel_credentials: grpc.ssl_channel_credentials = channel_credentials
        """
        The channel credentials to be used for TLS/SSL server 
        authentication, if required by the server (Default: None -> No TLS/SSL).

        Use :py:meth:`prosuite.utils.get_ssl_channel_credentials` to create the basic https 
        credentials if the appropria root certificates are in the windows certificate store.
        For advanced scenarios or credentials on a non-windows platform, see the gRPC Python docs
        (https://grpc.github.io/grpc/python/grpc.html).
        """

    def verify(
            self,
            specification: Union[Specification, XmlSpecification, DdxSpecification],
            perimeter: Union[EnvelopePerimeter, EsriShapePerimeter, WkbPerimeter] = None,
            output_dir: str = None,
            parameters: VerificationParameters = None
    ) -> Iterable[VerificationResponse]:
        """
        Executes a quality verification by running all quality conditions defined in the
        provided quality specification.

        Returns an iterator of VerificationResponse objects. Each response contains progress
        information, detected issues, and, in the final message, a complete VerifiedSpecification object.

        :param specification: The quality specification containing the conditions to be verified.
            Can be:
            - prosuite.quality.Specification (defined in Python)
            - prosuite.quality.DdxSpecification (from the data dictionary)
            - prosuite.quality.XmlSpecification (from an XML file)
        :param perimeter: Polygon/extent that defines the verification area.
            Default = None → full extent of verified datasets.
        :param output_dir: Optional output directory for results.
        :param parameters: Additional optional verification parameters.
        :return: Iterator of VerificationResponse objects.
        """

        # Build the internal advanced parameter object
        advanced_parameters = AdvancedParameters(specification, output_dir, perimeter, parameters)
        self._validate_params(advanced_parameters)

        # Create gRPC client and request
        channel = self._create_channel()
        client = qa_service.QualityVerificationGrpcStub(channel)
        request = self._compile_request(advanced_parameters)

        # Add objects to verify, if provided
        if parameters and parameters.objects_to_verify:
            if len(parameters.objects_to_verify) > 0:
                self._add_objects_to_verify(request, parameters.objects_to_verify)

        # Build a mapping: condition_id → condition_name (only works if IDs are available)
        cond_name_by_id = {
            c.id: c.name
            for c in specification.get_conditions()
            if getattr(c, "id", None)
        }

        last_message = ""

        # Iterate through streamed responses from the QA service
        for response_msg in client.VerifyQuality(request):
            progress = response_msg.progress

            # Determine message text and logging level
            if response_msg.progress.current_box.x_min > 0:
                msg = (
                    "Processing tile {current} of {total}: "
                    "XMin: {xmin} YMin: {ymin} XMax: {xmax} YMax: {ymax}"
                ).format(
                    current=progress.overall_progress_current_step,
                    total=progress.overall_progress_total_steps,
                    xmin=progress.current_box.x_min,
                    ymin=progress.current_box.y_min,
                    xmax=progress.current_box.x_max,
                    ymax=progress.current_box.y_max,
                )
                log_level = MessageLevel.level_40000  # Info
            elif progress.message:
                prefix = {
                    1: "Non-container processing: ",
                    2: "Container processing: "
                }.get(progress.progress_type, "")
                msg = prefix + progress.message
                log_level = progress.message_level
            else:
                msg = progress.processing_step_message
                log_level = progress.message_level

            # Avoid duplicate messages → downgrade to debug level
            if last_message == msg:
                log_level = MessageLevel.level_30000
            last_message = msg

            # Parse VerifiedSpecification only in final message
            verified_specification = None
            if response_msg.service_call_status == 3:  # Finished
                verified_specification = self._parse_verified_specification(response_msg, cond_name_by_id)

            yield VerificationResponse(
                service_call_status=response_msg.service_call_status,
                message=msg,
                message_level=log_level,
                issue_msgs=response_msg.issues,
                verified_specification=verified_specification
            )

    def _parse_verified_specification(
            self,
            response_msg,
            cond_name_by_id: dict[int, str]
    ) -> Optional[VerifiedSpecification]:
        """
        Extracts a VerifiedSpecification object from the final QA gRPC response msg.
        """
        qv = getattr(response_msg, "quality_verification", None)
        if not qv:
            return None

        verified_conditions = []
        cvs = getattr(qv, "condition_verifications", None)

        if cvs:
            for cv in cvs:
                cond_id = getattr(cv, "quality_condition_id", None)
                cond_name = cond_name_by_id.get(cond_id, "") if cond_id is not None else ""
                error_count = getattr(cv, "error_count", 0)

                verified_conditions.append(
                    VerifiedCondition(
                        condition_id=cond_id,
                        name=cond_name,
                        error_count=error_count
                    )
                )

        return VerifiedSpecification(
            specification_id=getattr(qv, "specification_id", None),
            specification_name=getattr(qv, "specification_name", ""),
            # context_name=getattr(qv, "context_name", ""),
            user_name=getattr(qv, "user_name", ""),
            verified_conditions=verified_conditions
        )

    def cancel(self, user_name: str, environment: str = "") -> bool:
        channel = grpc.insecure_channel(f'{self.host_name}:{self.port_nr}')
        stub = ProcessAdministrationGrpcStub(channel)

        cancel_request = CancelRequest(
            environment=environment or "",
            user_name=user_name
        )

        try:
            response = stub.Cancel(cancel_request)
            return response.success
        except grpc.RpcError as e:
            print(f"[ERROR] gRPC Cancel failed: {e.code()} - {e.details()}")
            return False

    def _create_channel(self):
        message_length = MAX_MESSAGE_LENGTH_MB * 1024 * 1024
        options = [('grpc.max_send_message_length', message_length),
                   ('grpc.max_receive_message_length', message_length)]

        if self.ssl_channel_credentials:
            channel = self._create_secure_channel(options)
        else:
            channel = grpc.insecure_channel(f'{self.host_name}:{self.port_nr}', options)
        return channel

    def _validate_params(self, params: AdvancedParameters):
        if params.output_dir is None:
            params.output_dir = ""
            logging.warning("No output dir is defined")
        if params.specification is None:
            raise Exception(
                "No specification is defined. Please assign verification.specification.")

    def _compile_request(self, parameters: AdvancedParameters):
        req = service_util.VerificationRequest()

        self._configure_verification_parameter_msg(req.parameters, parameters)
        self._configure_specification_msg(req, parameters.specification)
        req.max_parallel_processing = parameters.desired_parallel_processing
        req.user_name = parameters.user_name

        return req

    def _create_secure_channel(self, options) -> grpc.Channel:
        channel = grpc.secure_channel(
            f'{self.host_name}:{self.port_nr}', self.ssl_channel_credentials, options)
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            logging.info(
                f'Successfully established secure channel to {self.host_name}')
        except:
            logging.exception(
                f'Timeout. Failed to establish secure channel to {self.host_name}')
        return channel

    def _configure_specification_msg(self,
                                     verification_request: service_util.VerificationRequest,
                                     specification: Union[Specification, XmlSpecification, DdxSpecification]):

        quality_spec_msg = verification_request.specification

        if isinstance(specification, XmlSpecification):
            self._configure_xml_quality_specification_msg(quality_spec_msg.xml_specification, specification)
        elif isinstance(specification, DdxSpecification):
            self._configure_ddx_specification_msg(verification_request, specification)
        else:
            self._configure_condition_list_specification_msg(quality_spec_msg.condition_list_specification,
                                                             verification_request.work_context,
                                                             specification)

    def _configure_xml_quality_specification_msg(self,
                                                 xml_specification_msg: shared_qa.XmlQualitySpecificationMsg,
                                                 specification: XmlSpecification):
        xml_specification_msg.xml = specification.xml_string

        if (specification.specification_name is None):
            spec_name = ""
        else:
            spec_name = specification.specification_name

        xml_specification_msg.selected_specification_name = spec_name
        if specification.data_source_replacements:
            xml_specification_msg.data_source_replacements.extend(
                specification.data_source_replacements)
        return xml_specification_msg

    def _configure_condition_list_specification_msg(self,
                                                    cond_list_spec_msg: shared_qa.ConditionListSpecificationMsg,
                                                    work_context_msg: shared_qa.WorkContextMsg,
                                                    specification: Specification):

        cond_list_spec_msg.name = specification.name
        cond_list_spec_msg.description = specification.description

        for condition in specification.get_conditions():
            cond_list_spec_msg.elements.append(
                self._to_quality_specification_element_msg(condition))

        # If the catalog path of the model has been set (standalone verification), honor it:
        models = self._get_referenced_models(specification)

        for model in models:
            data_source_msg = shared_qa.DataSourceMsg()
            data_source_msg.id = model.id
            data_source_msg.model_name = model.name
            data_source_msg.catalog_path = model.catalog_path
            cond_list_spec_msg.data_sources.append(data_source_msg)

        if specification.project_short_name:
            # Use data dictionary instead of stand-alone verification.
            # Work context type 1 means project
            work_context_msg.type = 1
            work_context_msg.ddx_id = -1
            work_context_msg.context_name = specification.project_short_name

        return cond_list_spec_msg

    @staticmethod
    def _configure_ddx_specification_msg(verification_request: service_util.VerificationRequest,
                                         ddx_specification: DdxSpecification):

        specification_msg = verification_request.specification
        work_context_msg = verification_request.work_context

        specification_msg.quality_specification_id = ddx_specification.ddx_id

        # work context type 1 means project
        work_context_msg.type = 1
        work_context_msg.ddx_id = -1
        work_context_msg.context_name = ddx_specification.project_short_name

    def _configure_shape_msg(self,
                             shape_msg: shared_gdb.ShapeMsg,
                             perimeter: Union[EnvelopePerimeter, WkbPerimeter, EsriShapePerimeter]):
        if isinstance(perimeter, EnvelopePerimeter):
            perimeter: EnvelopePerimeter
            shape_msg.envelope.x_min = perimeter.x_min
            shape_msg.envelope.x_max = perimeter.x_max
            shape_msg.envelope.y_min = perimeter.y_min
            shape_msg.envelope.y_max = perimeter.y_max
        if isinstance(perimeter, EsriShapePerimeter):
            perimeter: EsriShapePerimeter
            shape_msg.esri_shape = perimeter.esri_shape
        if isinstance(perimeter, WkbPerimeter):
            perimeter: WkbPerimeter
            shape_msg.wkb = bytes(perimeter.wkb)

    def _to_quality_specification_element_msg(self, condition: Condition):

        spec_element = shared_qa.QualitySpecificationElementMsg()

        self._configure_quality_condition_msg(condition, spec_element.condition)

        spec_element.allow_errors = condition.issue_type == IssueType.Warning
        spec_element.category_name = condition.category
        spec_element.stop_on_error = condition.stop_on_error

        return spec_element

    def _configure_verification_parameter_msg(self,
                                              params_msg: shared_qa.VerificationParametersMsg,
                                              parameters: AdvancedParameters):

        params_msg.tile_size = parameters.tile_size
        params_msg.save_verification_statistics = parameters.save_verification_statistics
        params_msg.update_issues_in_verified_model = parameters.update_issues_in_verified_model

        if parameters.report_culture_code is not None:
            params_msg.report_culture_code = parameters.report_culture_code

        if parameters.output_dir != '':
            params_msg.issue_file_gdb_path = os.path.join(
                parameters.output_dir, Service.ISSUE_GDB)
            params_msg.html_report_path = os.path.join(
                parameters.output_dir, Service.HTML_REPORT)
            params_msg.verification_report_path = os.path.join(
                parameters.output_dir, Service.XML_REPORT)

        if parameters.perimeter:
            self._configure_shape_msg(
                params_msg.perimeter, parameters.perimeter)

    def _configure_quality_condition_msg(self,
                                         condition: Condition,
                                         condition_msg: shared_qa.QualityConditionMsg):
        condition_msg.name = condition.name
        condition_msg.test_descriptor_name = condition.test_descriptor
        condition_msg.description = condition.description
        condition_msg.url = condition.url
        condition_msg.condition_id = condition.id if condition.id else -1

        parameters = condition.parameters
        parameter_msgs = condition_msg.parameters

        self.configure_parameter_msgs(parameters, parameter_msgs)

    def _configure_transformer_msg(self,
                                   transformed_dataset: TransformedDataset,
                                   instance_config_msg: shared_qa.InstanceConfigurationMsg):

        instance_config_msg.name = transformed_dataset.name
        instance_config_msg.instance_descriptor_name = transformed_dataset.transformer_descriptor

        self.configure_parameter_msgs(transformed_dataset.parameters, instance_config_msg.parameters)

    def configure_parameter_msgs(self, parameters, parameter_msgs):

        for param in parameters:
            if param.contains_list_of_datasets:
                self._handle_dataset_list(parameter_msgs, param)
            else:
                parameter_msgs.append(self._to_parameter_mgs(param))

    def _handle_dataset_list(self,
                             parameter_msgs: list,
                             param: Parameter):
        """
        a Parameter value can be of type Dataset. Or it can be of type list[Dataset].
        if it is a Dataset list, each Dataset in the list should be treated as single Parameter
        """
        if param.contains_list_of_datasets:
            # in this case, param.dataset is actually a list of datasets. we need to unpack the list and create
            # single params for each dataset in the list
            if Parameter.value_is_list_of_datasets(param.dataset):
                for dataset in param.dataset:
                    ds_param = Parameter(param.name, dataset)
                    parameter_msgs.append(self._to_parameter_mgs(ds_param))

    def _to_parameter_mgs(self, param: Parameter):
        param_msg = shared_qa.ParameterMsg()
        param_msg.name = param.name

        if isinstance(param.dataset, TransformedDataset):
            # handle transformed dataset
            self._configure_transformer_msg(param.value, param_msg.transformer)
            param_msg.where_clause = Service._none_to_emtpy_str(param.get_where_clause())

        else:
            param_msg.value = Service._none_to_emtpy_str(
                param.get_string_value())
            param_msg.where_clause = Service._none_to_emtpy_str(
                param.get_where_clause())
            param_msg.workspace_id = param.get_workspace_id()
            param_msg.used_as_reference_data = False

        return param_msg

    @staticmethod
    def _none_to_emtpy_str(value) -> str:
        if value is None:
            return ""
        return value

    def _get_referenced_models(self, specification: Specification) -> list:
        result = set()  # Using a set to ensure distinct models

        for condition in specification.get_conditions():
            self._add_models_from_parameters(condition.parameters, result)

        return result

    def _add_models_from_parameters(self, parameters: list, result: set):
        """
        Extract models from a list of parameters and add them to the result set.
        
        :param parameters: The list of parameters to process
        :param result: Set to collect unique models
        """
        for parameter in parameters:
            if parameter.is_dataset_parameter():
                if parameter.contains_list_of_datasets:
                    for dataset in parameter.dataset:
                        model = dataset.model
                        if model not in result:
                            result.add(model)
                elif parameter.is_dataset_value():
                    # It's a dataset:
                    model = parameter.dataset.model
                    if model not in result:
                        result.add(model)
                elif parameter.is_transformed_dataset_value():
                    # It's a transformed dataset
                    transformed_dataset: TransformedDataset = parameter.value
                    self._add_models_from_parameters(transformed_dataset.parameters, result)

        return list(result)

    def _add_objects_to_verify(self, request, _objects_to_verify):
        for dataset_id, oid_list in _objects_to_verify.items():
            for oid in oid_list:
                gdb_object = shared_gdb.GdbObjectMsg(object_id=oid, class_handle=dataset_id)
                request.features.append(gdb_object)
