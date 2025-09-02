class Parameter:
    """
    A parameter configures a quality condition. Parameters can represent Datasets (dataset parameter) or scalar values
    (scalar parameters). Parameters have a name and a value.

    Dataset parameters: value is of type dataset. The parameter can retrieve the workspace id (model name or model id
    if it has been retrieved from the data dictionary) and the where clause (filter expression) of the dataset.

    Scalar parameters: value is a simple type (number, string, bool).
    """

    def __init__(self, name: str, value):
        self.contains_list_of_datasets = False
        self._dataset = None
        
        #:
        self.name: str = name
        """
        The parameter name.
        """

        #:
        self._value = None
        """
        The parameter value (private).
        """

        #:
        self._filter_expression = None
        """
        The dataset filter expression (private).
        """
        
        # Set the value using the setter to ensure consistency
        self.value = value
        
    @property
    def value(self):
        """
        The parameter value. Can be a dataset, transformed dataset, list of datasets, or a scalar value.
        """
        return self._value
        
    @value.setter
    def value(self, new_value):
        """
        Sets the parameter value and updates dataset property to maintain consistency.
        
        :param new_value: The new value to set
        """
        self._value = new_value
        
        # Update dataset property based on the new value
        # TODO: Make the handling of dataset lists more robust and consistent
        #       between the parameters coming from the data dictionary and the ones created in the code.
        if self._type_is_dataset(new_value):
            self._dataset = new_value
        else:
            self._dataset = None
            self.contains_list_of_datasets = False
            
    @property
    def dataset(self):
        """
        The dataset associated with this parameter (if any).
        """
        return self._dataset
        
    @dataset.setter
    def dataset(self, new_dataset):
        """
        Sets the dataset property and updates value property to maintain consistency.
        
        :param new_dataset: The new dataset value
        """
        self._dataset = new_dataset
        
        # When setting dataset, also update value
        if new_dataset is not None:
            self._value = new_dataset
            # Update contains_list_of_datasets flag
            self.contains_list_of_datasets = Parameter.value_is_list_of_datasets(new_dataset)

    def get_string_value(self) -> str:
        if self.dataset:
            if self.contains_list_of_datasets:
                return self.dataset[0].name
            else:
                return self.dataset.name
        else:
            if self.value is None:
                return ""
            else:
                return str(self.value)

    def is_dataset_parameter(self) -> bool:
        """
        Check if the parameter is a dataset parameter. A dataset parameter is a parameter that has a Dataset,
        a TransformedDataset or a list of datasets as its value.
        :return: True if the parameter is a dataset parameter, False otherwise.
        """
        if self.dataset:
            return True
        else:
            return False
        
    def is_dataset_value(self) -> bool:
        """
        Check if the parameter value is a Dataset (as opposed to a TransformedDataset or a list).
        :return: True if the parameter is a dataset parameter, False otherwise.
        """
        from prosuite.data_model import Dataset
        return self.dataset is not None and isinstance(self.dataset, Dataset)
        
    def is_transformed_dataset_value(self) -> bool:
        """
        Check if the parameter value is a TransformedDataset (as opposed to a Dataset or a list)."
        """
        from prosuite.data_model import TransformedDataset
        return self.dataset is not None and isinstance(self.dataset, TransformedDataset)

    def get_workspace_id(self):
        if self.is_dataset_value():
            return self.dataset.model.id
        else:
            return ""
        
    def get_where_clause(self):

        if self._filter_expression:
            return self._filter_expression
        if not self.dataset:
            return ""
        if self.contains_list_of_datasets:
            return self.dataset[0].filter_expression
        else:
            return self.dataset.filter_expression

    @staticmethod
    def value_is_list_of_datasets(value):
        from prosuite.data_model import BaseDataset
        if isinstance(value, list):
            if all(isinstance(x, BaseDataset) for x in value):
                return True
        return False

    def _type_is_dataset(self, value):
        from prosuite.data_model import BaseDataset
        if Parameter.value_is_list_of_datasets(value):
            self.contains_list_of_datasets = True
            return True
        if isinstance(value, BaseDataset):
            return True
        return False
