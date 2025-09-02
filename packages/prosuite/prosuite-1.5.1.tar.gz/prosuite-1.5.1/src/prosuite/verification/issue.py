from prosuite.verification import InvolvedTable
import prosuite.generated.quality_verification_service_pb2 as service_util
import prosuite.generated.quality_verification_service_pb2_grpc as qa_service
import prosuite.generated.shared_qa_pb2 as shared_qa
import prosuite.generated.shared_gdb_pb2 as shared_gdb


class Issue:
    """
    Represents an issue found during the verification.

    To initialize an Issue object, pass the issue message to it.
    The Issue object extracts some properties from the issue message and makes them available as attributes:
    """

    def __init__(self, issue_msg: shared_qa.IssueMsg):
        #:
        self.description = issue_msg.description
        """ The description of the issue."""
        #:
        self.involved_objects = list()
        """ A list of InvolvedTable objects that are involved in the issue."""
        #:
        self.geometry = issue_msg.issue_geometry
        """ The geometry involved of the issue."""
        #:
        self.issue_code = issue_msg.issue_code_id # TODO: test
        """ The issue code ID."""
        #:
        self.allowable = issue_msg.allowable # TODO: test
        """ If the issue is allowable."""
        #:
        self.stop_condition = issue_msg.stop_condition # TODO: test
        """ If the issue is a stop condition."""


        for involved_table_msg in issue_msg.involved_tables:
            involvedTable = InvolvedTable(involved_table_msg.table_name, involved_table_msg.object_ids)
            self.involved_objects.append(involvedTable)
