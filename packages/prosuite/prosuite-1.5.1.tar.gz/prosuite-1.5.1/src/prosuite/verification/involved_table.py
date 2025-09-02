class InvolvedTable:
    """
    Represents a table involved in a verification issue.
    """
    def __init__(self, table_name: str, object_ids: list):
        #:
        self.table_name = table_name
        """
        The name of the table.
        """
        #:
        self.object_ids = list(object_ids)
        """A list of object IDs from the table that are involved in the issue."""
