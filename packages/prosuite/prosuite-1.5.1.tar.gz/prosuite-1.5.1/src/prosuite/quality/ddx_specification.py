from typing import List


class DdxSpecification:
    """
    Represents a specification defined in the Data Dictionary (DDX). This requires a server that is configured
    with a data dictionary connection.
    """

    # TODO: Datasource replacements are not yet used. Consider converting them to some kind of work context
    #       (GDB version name, FGDB checkout).
    def __init__(self, ddx_id: int, project_short_name: str):

        self.ddx_id: int = ddx_id
        """
        ID of the specification in the data dictionary. Find out by using the properties window of the specification in the 
        data dictionary editor.
        """

        # Short name to be used in the WorkContextMsg
        self.project_short_name: str = project_short_name
        """
        Short name of the project in the data dictionary. This is used to determine the main main workspace of the verification. 
        In case the issues are written to the error datasets in the data model the project short name is used to determine the correct 
        error datasets. See :py:attr:`~verification.VerificationParameters.update_issues_in_verified_model`
        """

    @staticmethod
    def _parse_datasource_replacements(data_source_replacements: List[List[str]]):
        if data_source_replacements is None:
            return []  # Return an empty list if replacements are not provided
        result = []
        for pair in data_source_replacements:
            result.append(f"{pair[0]}|{pair[1]}")
        return result
