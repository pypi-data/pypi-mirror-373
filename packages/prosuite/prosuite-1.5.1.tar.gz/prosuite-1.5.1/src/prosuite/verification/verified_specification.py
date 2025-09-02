from typing import List, Optional
from prosuite.verification.verified_condition import VerifiedCondition


class VerifiedSpecification:
    """
    Represents the verified QA specification and its results.
    Includes metadata about the executed specification and all verified conditions.
    """

    def __init__(
            self,
            specification_id: Optional[int] = None,
            specification_name: str = "",
            # context_name: str = "",
            user_name: str = "",
            verified_conditions: Optional[List[VerifiedCondition]] = None,
    ):
        self.specification_id = specification_id
        """The ID of the verified specification or -1 in case if its not originated from the data dictionary."""

        self.specification_name = specification_name
        """The name of the verified specification."""

        # TODO Uniform handling not yet implemented

        # self.context_name = context_name
        # """Workspace / database context name."""

        self.user_name = user_name
        """User who executed the verification."""

        self.verified_conditions: List[VerifiedCondition] = verified_conditions or []
        """List of all verified QA conditions."""

    @property
    def verified_conditions_count(self) -> int:
        """Returns the number of verified QA conditions."""
        return len(self.verified_conditions)

    def __str__(self):
        return (
            f"VerifiedSpecification(Name='{self.specification_name}', "
            # f"Context='{self.context_name}', "
            f"User='{self.user_name}', "
            f"Conditions={self.verified_conditions_count})"
        )
