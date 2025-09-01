from frogml._proto.qwak.execution.v1.execution_pb2 import (
    ExecutionEntry as ProtoExecutionEntry,
)
from frogml._proto.qwak.execution.v1.execution_pb2 import (
    ExecutionStatus as ProtoExecutionStatus,
)
from frogml.core.clients.feature_store.execution_management_client import (
    ExecutionManagementClient,
)
from frogml.core.exceptions import FrogmlException


class ExecutionQuery:
    @staticmethod
    def _get_execution_status_name(proto_execution_status: ProtoExecutionStatus) -> str:
        """
        Translates between the execution status enum and front-end
        @param proto_execution_status:
        @type proto_execution_status:
        @return: str representation of the execution status
        @rtype: str
        """
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_FAILED:
            return "failed"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_QUEUED:
            return "queued"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_INVALID:
            return "invalid"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_PENDING:
            return "pending"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_RUNNING:
            return "running"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_CANCELLED:
            return "cancelled"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_COMPLETED:
            return "completed"
        if (
            proto_execution_status
            == ProtoExecutionStatus.EXECUTION_STATUS_FAILED_SUBMISSION
        ):
            return "failed submission"
        if proto_execution_status == ProtoExecutionStatus.EXECUTION_STATUS_SUBMITTED:
            return "submitted"
        else:
            "unsupported"

    @staticmethod
    def get_execution_status_message(execution_id: str) -> str:
        """
        This method receives an execution id and generates an appropriate status message according to its type and
        status.
        @param execution_id: execution id to query the status for
        @type execution_id: str
        @return: execution state message
        @rtype: str
        """
        execution_management_client = ExecutionManagementClient()
        entry_type: str = ""
        featureset_name: str = ""

        proto_execution_entry: ProtoExecutionEntry = (
            execution_management_client.get_execution_entry(
                execution_id=execution_id
            ).execution_entry
        )

        if proto_execution_entry.WhichOneof("execution_type") == "backfill_spec":
            featureset_name: str = proto_execution_entry.backfill_spec.featureset_name
            entry_type = "backfill"
        elif proto_execution_entry.WhichOneof("execution_type") == "batch_ingestion":
            featureset_name: str = proto_execution_entry.batch_ingestion.featureset_name
            entry_type = "batch job"
        else:
            raise FrogmlException(
                f"Entry for execution id {execution_id} is of unsupported type"
            )

        proto_execution_status: ProtoExecutionStatus = (
            execution_management_client.get_execution_status(
                execution_id=execution_id
            ).execution_status
        )

        execution_status_name: str = ExecutionQuery._get_execution_status_name(
            proto_execution_status
        )

        return (
            f"Execution id for a {entry_type} for featureset {featureset_name}, "
            f"status is {execution_status_name}"
        )
