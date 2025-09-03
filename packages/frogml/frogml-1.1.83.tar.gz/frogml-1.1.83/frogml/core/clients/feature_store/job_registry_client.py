import grpc
from dependency_injector.wiring import Provide

from frogml._proto.qwak.feature_store.jobs.v1.job_service_pb2 import (
    GetLatestJobRequest,
    GetLatestJobResponse,
    GetLatestSuccessfulJobRequest,
    GetLatestSuccessfulJobResponse,
)
from frogml._proto.qwak.feature_store.jobs.v1.job_service_pb2_grpc import JobServiceStub
from frogml.core.exceptions import FrogmlException, FrogmlNotFoundException
from frogml.core.inner.di_configuration import FrogmlContainer


class FeatureSetsJobRegistryClient:
    """
    Used for interacting with Feature Registry endpoints
    """

    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._job_registry = JobServiceStub(grpc_channel)

    def get_latest_successful_job(
        self, featureset_id: str, environment_id: str
    ) -> GetLatestSuccessfulJobResponse:
        """
        Args:
            featureset_id: The id of the requested featureset
            environment_id: The environment id of the requested featureset

        Returns:
            The response of the latest successful job
        """
        try:
            get_latest_successful_job_request = GetLatestSuccessfulJobRequest(
                featureset_id=featureset_id, environment_id=environment_id
            )
            return self._job_registry.GetLatestSuccessfulJob(
                get_latest_successful_job_request
            )
        except grpc.RpcError as e:
            if e.args[0].code == grpc.StatusCode.NOT_FOUND:
                raise FrogmlNotFoundException(
                    f"Resource was not found, error is {repr(e)}"
                )
            raise FrogmlException(
                f"Failed to get latest successful job, error is {repr(e)}"
            )

    def get_latest_job(
        self, featureset_id: str, environment_id: str
    ) -> GetLatestJobResponse:
        """
        Args:
            featureset_id: The id of the requested featureset
            environment_id: The environment id of the requested featureset

        Returns:
            The response of the latest successful job
        """
        try:
            get_latest_job_request = GetLatestJobRequest(
                featureset_id=featureset_id, environment_id=environment_id
            )
            return self._job_registry.GetLatestJob(get_latest_job_request)
        except grpc.RpcError as e:
            if e.args[0].code == grpc.StatusCode.NOT_FOUND:
                raise FrogmlNotFoundException(
                    f"Resource was not found, error is {repr(e)}"
                )
            raise FrogmlException(f"Failed to get latest job, error is {repr(e)}")
