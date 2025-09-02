from typing import List

from prosuite.utils.naming import create_name
from prosuite.quality import Parameter, IssueFilter, IssueType

class Condition:
    """
    A quality condition. Conditions are the primary building blocks of quality specifications.
    Each Condition is a configuration of a test algorithm for one or more datasets.
    Conditions must be created with the factory methods from :py:mod:`prosuite.factories.quality_conditions`
    """

    def __init__(self, test_descriptor: str, name: str = ""):

        #:
        self._id :int = None
        """
        Internal ID of the condition in the data dictionary (private).
        """

        #:
        self.name :str = name
        """
        The unique name of the quality condition.
        """

        #:
        self.test_descriptor :str = test_descriptor
        """
        The test descriptor, i.e. the algorithm used to verify this condition.
        """

        # NOTE: Issue type is not processed in the service, because on the server it is called allowed_errors (see above).
        self.issue_type: IssueType = IssueType.Error
        """
        Defines if a failing test returns a warning or an error issue. Quality conditions with 
        Issue Type = Warning are considered “soft” conditions, for which exceptions (“Allowed Issues”) may be defined.
        """

        #:
        self.category: str = ""
        """
        The name of the category, if this issue is assigned to a category.
        """

        #:
        self.stop_on_error: bool = False
        """
        Indicates if the occurrence of an error for an object should stop any further testing of the same object. 
        This can be used to prevent further tests on a feature after a serious geometry error (e.g. incorrectly 
        oriented rings) was detected for the feature.
        The used Test Descriptor provides a standard value for this property. It can optionally be overridden here.
        """

        #:
        self.description: str = ""
        """
        Freely definable description of the Quality Condition. This description can be displayed when viewing 
        issues in the issue navigator, and may contain explanations to the Quality Condition and instructions for 
        correcting the issues.
        """

        #:
        self.url: str = ""
        """
        Optional URL to a website providing additional information for this Quality Condition.
        Certain Quality Conditions require more detailed information about the test logic and/or the correction 
        guidelines than the field “Description” can provide. This information can for example be assembled in a 
        wiki, and the URL may be provided here. When viewing issues in the issue navigator, the corresponding web 
        page can be opened. In the HTML verification reports these URLs are used to render the names of the 
        Quality Conditions as links.
        """

        #:
        self.parameters: List[Parameter] = []
        """
        The list of parameters. Typically the parameters are specified in the factory method used to create the
        quality condition (see :py:mod:`prosuite.factories.quality_conditions`) and do not need to be changed
        through this list.
        """
        
        #:
        self.issue_filters: List[IssueFilter] = []
        """
        The list of issue filters for this condition.
        """

        #:
        self.issue_filter_expression: str
        """
        The filter expression to be used for multiple issue_filters.
        """

    @property
    def id(self) -> int:
        """
        The unique identifier of the condition in the data dictionary, or None if
        it has not been loaded from the data dictionary.
        This property is read-only.
        """
        return self._id

    def generate_name(self):
        """
        Generates a technical name using the dataset name(s) and the test descriptor. This is the default name of
        a condition if it was created by the standard factory method from :py:mod:`prosuite.factories.quality_conditions`.
        """
        descriptor = self.test_descriptor
        params = self.parameters

        self.name = create_name(descriptor, params)
