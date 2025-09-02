from prosuite.verification import Issue
from prosuite.verification.message_level import MessageLevel
from prosuite.verification.service_status import ServiceStatus
from prosuite.verification.verified_specification import VerifiedSpecification
from typing import Optional


class VerificationResponse:
    """
    This class represents a VerificationResponse Message.
    The str() method is overridden to return all properties from the VerificationResponse when
    a VerificationResponse object is printed using pythons print() method.
    """

    def __init__(self, service_call_status: str, message: str, message_level: str, issue_msgs: list, verified_specification: Optional[VerifiedSpecification] = None,
):
        #:
        self.message: str = message
        """the actual message"""
        #:
        self.service_call_status = ServiceStatus.status_0
        """service status -> see class ServiceStatus"""
        #:
        self.message_level = MessageLevel.level_40000
        """message level -> see class MessageLevel"""

        self.issues: list[Issue] = []
        """List of issues"""

        self.verified_specification = verified_specification
        """Optional object containing metadata and results of the verified QA specification."""
        #:
        self._set_service_call_status(service_call_status)
        #:
        self._set_message_level(message_level)
        #:

        for issue_msg in issue_msgs:
            self.issues.append(Issue(issue_msg))

    def __str__(self):
        return f'service_call_status: {self.service_call_status}\t message_level: {self.message_level} \t ' \
               f'message: {self.message}'

    def _set_service_call_status(self, service_call_status: str):
        if service_call_status == 0:
            self.service_call_status = ServiceStatus.status_0
        if service_call_status == 1:
            self.service_call_status = ServiceStatus.status_1
        if service_call_status == 2:
            self.service_call_status = ServiceStatus.status_2
        if service_call_status == 3:
            self.service_call_status = ServiceStatus.status_3
        if service_call_status == 4:
            self.service_call_status = ServiceStatus.status_4

    def _set_message_level(self, message_level: str):
        if message_level == 110000:
            self.message_level = MessageLevel.level_110000
        if message_level == 70000:
            self.message_level = MessageLevel.level_70000
        if message_level == 60000:
            self.message_level = MessageLevel.level_60000
        if message_level == 40000:
            self.message_level = MessageLevel.level_40000
        if message_level == 30000:
            self.message_level = MessageLevel.level_30000
        if message_level == 10000:
            self.message_level = MessageLevel.level_10000
