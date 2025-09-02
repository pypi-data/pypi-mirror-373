from typing import List
from prosuite.data_model import TransformedDataset
from prosuite.data_model.dataset import Dataset
from prosuite.data_model.model import Model
from prosuite.quality import Parameter, Condition, Specification
import prosuite.generated.quality_verification_ddx_pb2 as service_util
import prosuite.generated.quality_verification_ddx_pb2_grpc as ddx_service

from prosuite.generated.shared_qa_pb2 import InstanceConfigurationMsg, ParameterMsg, QualityConditionMsg
from prosuite.generated.shared_ddx_pb2 import DatasetMsg

from prosuite.quality.issue_filter import IssueFilter
from prosuite.utils.proto import create_dataset_from_proto, create_dataset_parameter_from_proto, create_model_from_proto

import grpc
import logging

MAX_MESSAGE_LENGTH_MB = 1024

class DdxService:
    """
    The service class communicates on the http/2 channel with the server and provides 
    access to the data dictionary, the ProSuite configuration database.
    """

    def __init__(self, host_name: str, port_nr: int, channel_credentials: grpc.ssl_channel_credentials = None):
        #:
        self.host_name = host_name
        """
        The name or IP address of the host running the service.
        """
        #:
        self.port_nr = port_nr
        """
        The port used by the service.
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

        #:
        self.ddx_environment = None
        """
        The data dictionary environment to be used for the service calls. This is only relevant if
        multiple environments are served by the service.
        """

    def get_specification(self, ddx_specification_id: int) -> Specification:
        """
        Loads the detailed quality specification from the data dictionary.
        Returns a Specification containing the detailed conditions.

        Please refer to the :ref:`samples <samples-link>` for more details.

        :param ddx_specification_id: The data dictionary quality specification id.
        :return: The specification containing the detailed conditions.
            It can be adapted in code and used in a quality verification.
        :rtype: Specification
        """

        channel = self._create_channel()

        client = ddx_service.QualityVerificationDdxGrpcStub(channel)

        request = self._compile_request(ddx_specification_id)

        response_msg:service_util.GetSpecificationResponse = client.GetQualitySpecification(request)

        models_by_id = dict()
        for model_msg in response_msg.referenced_models:
            model =  create_model_from_proto(model_msg)

            model_id = int(model.id)
            models_by_id[model_id] = model

        datasets_by_id = dict()
        for dataset_msg in response_msg.referenced_datasets:

            dataset = self._create_dataset(models_by_id, dataset_msg)
            datasets_by_id[dataset_msg.dataset_id] = dataset

        ddx_specification = self._unpack_specification(response_msg, models_by_id)

        return ddx_specification

    def _create_dataset(self, models_by_id, dataset_msg: DatasetMsg) -> Dataset:

        if dataset_msg.model_id == 0:
            print(f"Warning: Dataset has no model: {dataset_msg.name}")

        model:Model = models_by_id[dataset_msg.model_id]
        dataset = create_dataset_from_proto(dataset_msg, model)
        return dataset


    def _create_channel(self):
        message_length = MAX_MESSAGE_LENGTH_MB * 1024 * 1024
        options=[('grpc.max_send_message_length', message_length),
                 ('grpc.max_receive_message_length', message_length)]
        
        if self.ssl_channel_credentials:
            channel = self._create_secure_channel(options)
        else:
            channel = grpc.insecure_channel(f'{self.host_name}:{self.port_nr}', options)
        return channel

    def _compile_request(self, ddx_specification_id: int) -> service_util.GetSpecificationRequest:

        req = service_util.GetSpecificationRequest()

        req.quality_specification_id = ddx_specification_id

        if (self.ddx_environment is not None):
            req.environment = self.ddx_environment
        
        return req
    

    def _unpack_specification(self, response_msg, models_by_id) -> Specification:
        """
        Unpacks the specification from the response message.

        :param response_msg: The response message containing the specification.
        :return: The unpacked specification.
        :rtype: Specification
        """
        
        specification = Specification()

        specification_msg = response_msg.specification

        specification.name = specification_msg.name
        specification.description = specification_msg.description

        # for each element in the response message, create a new condition object
        for element_msg in specification_msg.elements:
            condition_msg:QualityConditionMsg = element_msg.condition

            condition:Condition = Condition(condition_msg.test_descriptor_name, condition_msg.name)

            condition._id = condition_msg.condition_id
            condition.description = condition_msg.description
            condition.url = condition_msg.url

            from prosuite.quality.condition import IssueType
            condition.issue_type = IssueType.Warning if element_msg.allow_errors else IssueType.Error
            condition.category = element_msg.category_name
            condition.stop_on_error = element_msg.stop_on_error

            parameters = self._unpack_parameter_values(condition_msg.parameters, models_by_id)
            condition.parameters = parameters

            for issue_filter_msg in condition_msg.condition_issue_filters:
                issue_filter = self._unpack_issue_filter(issue_filter_msg, models_by_id)
                condition.issue_filters.append(issue_filter)

            condition.issue_filter_expression = condition_msg.issue_filter_expression

            specification.add_condition(condition)

        return specification

    def _unpack_issue_filter(self, issue_filter_msg:InstanceConfigurationMsg, models_by_id) -> IssueFilter:
        """
        Unpacks an issue filter message into an IssueFilter object.
        
        :param issue_filter_msg: The issue filter message from the protobuf response.
        :param models_by_id: Dictionary mapping model IDs to Model objects.
        :return: An IssueFilter object.
        :rtype: IssueFilter
        """
        issue_filter = IssueFilter(issue_filter_msg.instance_descriptor_name, issue_filter_msg.name)
        
        # Set basic properties
        issue_filter._id = issue_filter_msg.id
        issue_filter.description = issue_filter_msg.description
        
        issue_filter_msg.parameters = self._unpack_parameter_values(issue_filter_msg.parameters, models_by_id)

        return issue_filter

    def _unpack_parameter_values(self, parameter_msgs:List[ParameterMsg], models_by_id) -> List[Parameter]:

        parameters: List[Parameter] = []
        
        for param_msg in parameter_msgs:
            result = self._unpack_parameter_value(param_msg, models_by_id)
            parameters.append(result)

        return parameters

    def _unpack_parameter_value(self, param_msg, models_by_id):

        result:Parameter = None

        transformer:InstanceConfigurationMsg = param_msg.transformer

        if (transformer.name != ''):
            # It's a transformer
            transformed_dataset = TransformedDataset(transformer.instance_descriptor_name, transformer.name, param_msg.where_clause)
            transformed_dataset.parameters = self._unpack_parameter_values(transformer.parameters, models_by_id)
            
            result = Parameter(param_msg.name, transformed_dataset)
            result._filter_expression = param_msg.where_clause

        elif (param_msg.workspace_id != ''):
            # It's a dataset
            result = create_dataset_parameter_from_proto(param_msg, models_by_id)

        else:
            result = Parameter(param_msg.name, param_msg.value)

        return result


    def _create_secure_channel(self, options) -> grpc.Channel:
        channel = grpc.secure_channel(
            f'{self.host_name}:{self.port_nr}', self.ssl_channel_credentials, options)
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            logging.info(
                f'Successfully established secure channel to {self.host_name}')
        except Exception as e:
            logging.exception(
                f'Timeout. Failed to establish secure channel to {self.host_name}: {e}')
        return channel

