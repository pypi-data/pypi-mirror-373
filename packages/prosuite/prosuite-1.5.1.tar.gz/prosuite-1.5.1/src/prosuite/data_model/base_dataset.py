class BaseDataset:
    """
    The base class for datasets representing tabular data. It is either a :class:`.Dataset` or, in the future, a :class:`.TransformedDataset`
    """
    def __init__(self, name: str, filter_expression: str = ""):

        #:
        self.name: str = name
        """
        The name of the dataset. Must be unique with respect to all other datasets of the model.
        """

        self.filter_expression: str = filter_expression
        pass
