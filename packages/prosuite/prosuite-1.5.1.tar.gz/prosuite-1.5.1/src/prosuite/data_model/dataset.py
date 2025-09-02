from prosuite.data_model import BaseDataset, Model

class Dataset(BaseDataset):
    """
    A dataset represents data from a table or feature class in a workspace, optionally filtered by an SQL expression.

    :param name: table or featureclass name
    :type name: str
    :param model: The :class:`prosuite.data_model.Model` this dataset belongs to.
    :type model: class:`prosuite.data_model.Model`
    :param filter_expression: A where clause that filters the table. The syntax of the where clause is defined in
        the document SQLSyntax_en.pdf
    :type filter_expression: str, optional
    """

    def __init__(self, name: str, model: Model, filter_expression: str = ""):
        super().__init__(name, filter_expression)

        #:
        self.model: Model = model
        """
        The dataset's data model.
        """

        #: 
        self._id: int = None
        """
        Internal ID of the dataset (private).
        """

        #:
        self._alias_name: str = None
        """
        Alias name of the dataset (private).
        """

        self.model.add_dataset(self)

    @property
    def id(self) -> int:
        """
        The unique identifier of the dataset in the data dictionary, or None it 
        has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._id
    
    @property
    def alias_name(self) -> str:
        """
        The alias name of the dataset in the data dictionary, or None it 
        has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._alias_name
    
    def __eq__(self, other):
        """
        Compare two datasets for equality.
        
        Datasets are considered equal if they:
        1. Have the same ID (if IDs are assigned)
        2. Or have the same name, model and filter expression (if IDs are not assigned)
        
        :param other: Another dataset to compare with
        :return: True if the datasets are equal, False otherwise
        """
        if not isinstance(other, Dataset):
            return False
                   
        # Compare name, model
        return (self.name == other.name and 
                self.model == other.model)

    def __hash__(self):
        """
        Return a hash value for the dataset as it required when implementing 
        __eq__ to maintain expected behavior with sets and dictionaries.
        
        :return: Hash value for the dataset
        """
        return hash(self.name, hash(self.model) if self.model else None)
    
