import grpc
from dependency_injector.wiring import Provide

from frogml._proto.qwak.deployment.alert_pb2 import (
    NotificationChannel,
    NotificationChannelSettings,
)
from frogml._proto.qwak.deployment.alert_service_pb2 import (
    ApplyNotificationChannelRequest,
    DeleteNotificationChannelRequest,
    GetNotificationChannelDetailsListRequest,
)
from frogml._proto.qwak.deployment.alert_service_pb2_grpc import (
    AlertManagementServiceStub,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.inner.di_configuration import FrogmlContainer


class AlertsManagementClient:
    def __init__(self, grpc_channel=Provide[FrogmlContainer.core_grpc_channel]):
        self._alerts_management_service = AlertManagementServiceStub(grpc_channel)

    def configure_channel(
        self, channel_name: str, notification_settings: NotificationChannelSettings
    ):
        try:
            self._alerts_management_service.ApplyNotificationChannel(
                ApplyNotificationChannelRequest(
                    notification_channel=NotificationChannel(
                        notification_channel_name=channel_name,
                        notification_settings=notification_settings,
                    ),
                )
            )

        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to save notification channel, error is {e.details()}"
            )

    def list_channels(self):
        try:
            return self._alerts_management_service.GetNotificationChannelDetailsList(
                GetNotificationChannelDetailsListRequest()
            )

        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to fetch notification channels, error is {e.details()}"
            )

    def delete_channel(self, notification_channel_id):
        try:
            self._alerts_management_service.DeleteNotificationChannel(
                DeleteNotificationChannelRequest(
                    notification_channel_id=notification_channel_id
                )
            )

        except grpc.RpcError as e:
            raise FrogmlException(
                f"Failed to delete notification channel, error is {e.details()}"
            )
