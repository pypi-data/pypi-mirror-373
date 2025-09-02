import typing

from prosuite.quality import Condition


class Specification:
    """
    Represents a quality specification defined in code. Quality specifications are collections of quality conditions.

    :param name: specification name
    :type name: str
    :param description: specification description
    :type description: str
    """

    def __init__(self, name: str = 'Custom Specification', description: str = ''):
        self._conditions: typing.List[Condition] = []
        self.name = name
        self.description = description

        # Short name to be used in the WorkContextMsg
        self.project_short_name: str = None
        """
        Short name of the project in the data dictionary. If the project short name is provided, the datasets registered in the data
        dictionary are used. Otherwise, the datasets are retrieved using the provided catalog path of the datasets' model. 
        The project short name is also used to determine the main workspace of the verification.
        The project short name is also used to determine the correct error datasets in the data model in case the issues are stored 
        in the error datasets of the data model. See :py:attr:`~verification.VerificationParameters.update_issues_in_verified_model`
        In case the issues are written to the error datasets in the data model the project short name is used to determine the correct 
        error datasets. See :py:attr:`~verification.VerificationParameters.update_issues_in_verified_model`
        """

    def add_condition(self, condition: Condition):
        """
        Adds conditions to the specification
        """
        self._conditions.append(condition)

    def get_conditions(self) -> typing.List[Condition]:
        """
        Returns the List of conditions
        """
        return self._conditions
