class VerifiedCondition:
    """
    Represents a verified QA condition, including its ID, name, and error count.
    """

    def __init__(self, condition_id: int = None, name: str = "", error_count: int = 0):
        #:
        self.condition_id: int | None = condition_id
        """
        The unique identifier of the condition in the data dictionary, or None if
        it has not been loaded from the data dictionary.
        """        #:
        self.name: str = name
        """The name of the verified quality condition (empty string if unavailable)."""
        #:
        self.error_count: int = error_count
        """Number of detected issues (errors) for this condition."""

    def __str__(self):
        return f"VerifiedCondition(ID={self.condition_id}, Name='{self.name}', Errors={self.error_count})"
