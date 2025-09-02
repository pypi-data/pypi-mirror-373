from typing import List

from prosuite.quality import Parameter
from prosuite.utils.naming import create_name


class IssueFilter:
    """
    An issue filter optionally filters issues found by a quality condition by configurable
    criteria. Its purpose is the reduction of false positives. Each quality condition can
    have none, one or multiple issue filters.

    :param issue_filter_descriptor: The issue filter descriptor, i.e. the algorithm used to 
        filter issues found by the condition.
    :type issue_filter_descriptor: str
    :param name: name of the issue filter
    :type name: str
    """

    def __init__(self, issue_filter_descriptor: str, name: str = ""):
        #:
        self.issue_filter_descriptor: str = issue_filter_descriptor
        """
        The issue filter descriptor, i.e. the algorithm used to filter the issues.
        """
        
        #:
        self.name: str = name
        """
        The (unique) name of the issue filter.
        """
        
        #:
        self._id: int = None
        """
        Internal ID of the issue filter in the data dictionary (private).
        """
        
        #:
        self.description: str = ""
        """
        The description of the issue filter.
        """
        
        #:
        self.parameters: List[Parameter] = []
        """
        The list of parameters. Typically the parameters are specified in the factory method used to create the
        issue filter (see :py:mod:`prosuite.factories.issue_filters`) and do not need to be changed
        through this list.
        """

    @property
    def id(self) -> int:
        """
        The unique identifier of the issue filter in the data dictionary, or None if
        it has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._id

    def generate_name(self):
        """
        Generates a technical name using the dataset name(s) and the test descriptor. This is the default name of
        a condition if it was created by the standard factory method from :py:mod:`prosuite.factories.quality_conditions`.
        """
        descriptor = self.issue_filter_descriptor
        params = self.parameters

        self.name = create_name(descriptor, params)
