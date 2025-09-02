from datetime import datetime
from prosuite.data_model import BaseDataset
from prosuite.utils.naming import create_name


class TransformedDataset(BaseDataset):
    """
    A transformed dataset represents tabular data that has been transformed from other input 
    tables or feature classes, optionally filtered by an SQL expression.

    :param transformer_descriptor: The transformer descriptor, i.e. the algorithm used to 
        generate this dataset.
    :type transformer_descriptor: str
    :param name: name of the transformed table or featureclass
    :type name: str
    :param filter_expression: A where clause that filters the table. The syntax of the where 
        clause is defined in the document SQLSyntax_en.pdf
    :type filter_expression: str, optional
    """

    def __init__(self, transformer_descriptor: str, name: str = "", filter_expression: str = ""):
        from prosuite.quality.parameter import Parameter
        from typing import List
        super().__init__(name, filter_expression)

        #:
        self.name = name
        """
        The unique name of the transformed dataset.
        """
        
        #:
        self.transformer_descriptor = transformer_descriptor
        """
        The transformer descriptor, i.e. the algorithm used to generate this dataset.
        """

        self.parameters: List[Parameter] = []
        """
        The list of parameters. Typically the parameters are specified in the factory method used to create the
        transformed dataset (see :py:mod:`prosuite.factories.transformers.Transformers`) and do not need to be changed
        through this list.
        """

    def generate_name(self):
        """
        Generates a technical name using the dataset name(s) and the transformer descriptor. This is the default name of
        a transformed dataset if it was created by the standard factory method from :py:mod:`prosuite.factories.transformers`.
        """
        descriptor = self.transformer_descriptor
        params = self.parameters

        self.name = create_name(descriptor, params)

    def generate_name_with_timestamp(self):
        """
        Generates a technical name using the dataset name(s) and the transformer descriptor,
        and appends a timestamp to ensure uniqueness.
        """
        descriptor = self.transformer_descriptor
        params = self.parameters

        base_name = create_name(descriptor, params)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.name = f"{base_name}_{timestamp}"

