from prosuite.data_model.dataset import Dataset
from prosuite.data_model.model import Model
from prosuite.generated.shared_ddx_pb2 import DatasetMsg, ModelMsg
from prosuite.generated.shared_gdb_pb2 import SpatialReferenceMsg
from prosuite.generated.shared_qa_pb2 import ParameterMsg
from prosuite.quality.parameter import Parameter

# Connection type constants
type_fgdb = 1
type_filesystem = 2
type_sdefile = 3
type_connection_properties = 4
type_sqlite = 5
type_service = 6

def create_model_from_proto(model_msg: ModelMsg) -> Model:
    """
    Create a model from a protobuf model message. Used internally.
    """

    result = Model(model_msg.name, '')
    result._id = model_msg.model_id

    spatial_reference_msg:SpatialReferenceMsg = model_msg.spatial_reference

    if (spatial_reference_msg.spatial_reference_wkid != 0):
        result._wkid = spatial_reference_msg.spatial_reference_wkid

    result._default_database_schema_owner = model_msg.default_database_schema_owner
    result._default_database_name = model_msg.default_database_name

    result._element_names_are_qualified  = model_msg.element_names_are_qualified

    connection_type = model_msg.user_connection.connection_type
    if connection_type in [type_fgdb, type_sdefile, type_sqlite]:
        result.catalog_path = model_msg.user_connection.connection_string

    return result

@staticmethod
def create_dataset_from_proto(dataset_msg: DatasetMsg, model: Model) -> Dataset:
    """
    Create a dataset from a protobuf dataset message. Used internally.
    """

    result = Dataset(dataset_msg.name, model, '')

    result._id = dataset_msg.dataset_id
    result._alias_name = dataset_msg.alias_name

    # TODO: Dataset Type, Geometry Type, 
    
    return result

@staticmethod
def create_dataset_parameter_from_proto(parameter_msg: ParameterMsg, models_by_id) -> Parameter:
    """
    Create a model from a protobuf model message. Used internally.
    """
    if parameter_msg.workspace_id == '':
        raise ValueError(f"The provided parameter message {parameter_msg.name} with value {parameter_msg.value} is not a dataset parameter.")
    
    model_id = int(parameter_msg.workspace_id)
    model: Model = models_by_id[model_id]
    dataset = model.get_dataset_by_name(parameter_msg.value)
    assert dataset is not None, f"Dataset with name {parameter_msg.name} not found in model {model.name}"

    result:Parameter = Parameter(parameter_msg.name, dataset)
    result._filter_expression = parameter_msg.where_clause

    return result
