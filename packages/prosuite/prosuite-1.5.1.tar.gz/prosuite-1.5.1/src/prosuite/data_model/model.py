from typing import Optional


class Model:
    """
    The Model represents the data model in a workspace (file-gdb or enterprise-gdb)

    :param name: name of the model
    :type name: str
    :param catalog_path: The catalog path of the associated workspace.
    :type name: str
    
    catalog_path examples:
        c:/data.gdb
        c:/enterprise_gdb.sde
    """

    def __init__(self, name, catalog_path):

        #:
        self.name: str = name
        """
        The unique name of the model.
        """
        #:
        self.catalog_path: str = catalog_path
        """
        The catalog path of the associated workspace.
        """

        #: 
        self._id: Optional[int] = None
        """
        Internal ID of the model (private).
        """
        
        #:
        self._wkid: Optional[int] = None
        """
        Spatial reference WKID of the model (private).
        """

        #:
        self._default_database_schema_owner: Optional[str] = None
        """
        Default database schema owner (private).
        """
        
        #:
        self._default_database_name: Optional[str] = None
        """
        Default database name (private).
        """
        
        #:
        self._element_names_are_qualified: bool = True
        """
        Whether model element names (datasets, associations) are qualified (private).
        """

        #:
        self.datasets = []
        """
        List of datasets in the model.
        """

    @property
    def id(self) -> str:
        """
        The unique identifier of the model in the data dictionary, or None it
        has not been loaded from the data dictionary.
        This property is read-only.
        """
        if self._id is not None:
            return str(self._id)

        # If it doesn't come from the DDX, there is no id and we use the name
        return self.name


        
    @property
    def wkid(self) -> int:
        """
        The spatial reference well-known ID (WKID) for the model as defined in 
        the data dictionary, or None it has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._wkid
        
    @property
    def default_database_schema_owner(self) -> str:
        """
        Gets the default database schema owner for this model as defined in 
        the data dictionary, or None it has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._default_database_schema_owner
        
    @property
    def default_database_name(self) -> str:
        """
        Gets the default database name for this model as defined in 
        the data dictionary, or None it has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._default_database_name
        
    @property
    def element_names_are_qualified(self) -> bool:
        """
        Gets whether Whether model element names (datasets, associations) are qualified in this model.
        For models not loaded from the data dictionary always fully qualify dataset/table names from
        RDBMS.
        This property is read-only.
        """
        return self._element_names_are_qualified
    
    def add_dataset(self, dataset):
        """
        Add a dataset to the model.
        """
        if (dataset not in self.datasets):
            self.datasets.append(dataset)

    def get_dataset_by_name(self, name):
        """
        Get a dataset from this model by its name.
        """
        for dataset in self.datasets:
            if dataset.name == name:
                return dataset
        return None
    
    def __hash__(self):
        """
        Returns a hash value for the model based on its name and id.
        These attributes are chosen as they should uniquely identify a model.
        Using None for id is valid and will be handled consistently.
        """
        return hash((self.name, self._id))

    def __eq__(self, other):
        """
        Checks if two Model instances are equal based on name and id.
        """
        if not isinstance(other, Model):
            return False
        return self.name == other.name and self._id == other._id

    def __ne__(self, other):
        """
        Checks if two Model instances are not equal.
        """
        return not self.__eq__(other)
