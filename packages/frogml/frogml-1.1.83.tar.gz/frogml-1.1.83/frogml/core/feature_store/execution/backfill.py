from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from google.protobuf.timestamp_pb2 import Timestamp as ProtoTimetamp

from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    AsScheduledBackfillType as ProtoAsScheduledBackfillType,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    BackfillSpec as ProtoBackfillSpec,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    BackfillType as ProtoBackfillType,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    ExplicitResourceConfiguration as ProtoExplicitResourceConfiguration,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    FullResetBackfillWindow as ProtoFullResetBackfillWindow,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    ImplicitResourceConfiguration as ProtoImplicitResourceConfiguration,
)
from frogml._proto.qwak.execution.v1.backfill_pb2 import (
    IntervalBackfillWindow as ProtoIntervalBackfillWindow,
)
from frogml.core.clients.feature_store.execution_management_client import (
    ExecutionManagementClient,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.feature_store.feature_sets.execution_spec import ClusterTemplate


@dataclass()
class IntervalBackfillWindow:
    @staticmethod
    def to_proto(
        backfill_start: datetime, backfill_end: datetime
    ) -> ProtoIntervalBackfillWindow:
        proto_backfill_start_timestamp = ProtoTimetamp()
        proto_backfill_start_timestamp.FromDatetime(backfill_start)

        proto_backfill_end_timestamp = ProtoTimetamp()
        proto_backfill_end_timestamp.FromDatetime(backfill_end)

        return ProtoIntervalBackfillWindow(
            backfill_start=proto_backfill_start_timestamp,
            backfill_end=proto_backfill_end_timestamp,
        )


@dataclass()
class FullResetBackfillWindow:
    @staticmethod
    def to_proto() -> Optional[ProtoFullResetBackfillWindow]:
        return ProtoFullResetBackfillWindow()


@dataclass()
class ImplicitResourceConfiguration:
    @staticmethod
    def to_proto() -> ProtoImplicitResourceConfiguration:
        return ProtoImplicitResourceConfiguration()


@dataclass()
class ExplicitResourceConfiguration:
    @staticmethod
    def _get_cluster_template(cluster_template_str: str) -> Optional[ClusterTemplate]:
        if cluster_template_str:
            try:
                return ClusterTemplate(cluster_template_str.upper())
            except ValueError:
                raise FrogmlException(
                    f"Received an unsupported cluster template size {cluster_template_str.upper()}"
                )
        return None

    @classmethod
    def to_proto(cls, cluster_template_str: str) -> ProtoImplicitResourceConfiguration:
        cluster_template = cls._get_cluster_template(cluster_template_str)
        return ProtoExplicitResourceConfiguration(
            cluster_template=ClusterTemplate.to_proto(cluster_template)
        )


@dataclass()
class BackfillType(ABC):
    @staticmethod
    @abstractmethod
    def to_proto() -> ProtoBackfillType:
        pass


@dataclass()
class AsScheduledBackfillType(BackfillType):
    @staticmethod
    def to_proto() -> ProtoBackfillType:
        return ProtoBackfillType(as_scheduled=ProtoAsScheduledBackfillType())


@dataclass()
class Backfill:
    def __init__(
        self,
        featureset_name: str,
        start_time: Optional[datetime] = None,
        stop_time: Optional[datetime] = None,
        cluster_template: str = "",
        comment: str = "",
    ):
        self._execution_management_client = self._get_execution_management_client()
        self.featureset_name = featureset_name
        self.start_time = start_time
        self.stop_time = stop_time
        self.cluster_template = cluster_template
        self.comment = comment

    @staticmethod
    def _get_execution_management_client() -> ExecutionManagementClient:
        return ExecutionManagementClient()

    def _generate_backfill_spec_proto(self) -> ProtoBackfillSpec:
        explicit_configuration: Optional[ProtoExplicitResourceConfiguration] = None
        no_override: Optional[ProtoImplicitResourceConfiguration] = None
        interval_backfill: Optional[ProtoIntervalBackfillWindow] = None
        full_reset_backfill: Optional[ProtoFullResetBackfillWindow] = None
        backfill_type: ProtoBackfillType = AsScheduledBackfillType.to_proto()

        if self.cluster_template:
            explicit_configuration = ExplicitResourceConfiguration.to_proto(
                cluster_template_str=self.cluster_template
            )
        else:
            no_override = ImplicitResourceConfiguration.to_proto()

        if self.start_time or self.stop_time:
            interval_backfill = IntervalBackfillWindow.to_proto(
                backfill_start=self.start_time, backfill_end=self.stop_time
            )
        else:
            full_reset_backfill = FullResetBackfillWindow.to_proto()

        return ProtoBackfillSpec(
            featureset_name=self.featureset_name,
            interval_backfill=interval_backfill,
            full_reset_backfill=full_reset_backfill,
            comment=self.comment,
            backfill_type=backfill_type,
            no_override=no_override,
            explicit_configuration=explicit_configuration,
        )

    def trigger_batch_backfill(self) -> str:
        proto_backfill_spec: ProtoBackfillSpec = self._generate_backfill_spec_proto()

        return self._execution_management_client.trigger_batch_backfill(
            batch_backfill_spec=proto_backfill_spec
        ).execution_id

    @staticmethod
    def generate_expected_ticks_repr(
        start_time: datetime, stop_time: datetime, scheduling_policy: str
    ) -> List[str]:
        import croniter

        cron_ticks: List[datetime] = [
            t
            for t in croniter.croniter_range(
                start=start_time,
                stop=stop_time,
                expr_format=scheduling_policy,
                exclude_ends=False,
            )
        ]

        if not cron_ticks:
            cron_ticks = [start_time, stop_time.replace(microsecond=0)]
        else:
            if cron_ticks[0] > start_time:
                cron_ticks.insert(0, start_time)
            if cron_ticks[len(cron_ticks) - 1] < stop_time:
                cron_ticks.append(stop_time.replace(microsecond=0))

        def stitch(x: datetime, y: datetime) -> str:
            return f"{x.isoformat()} -> {y.isoformat()}"

        zipped_tick_strs: List[str] = [
            stitch(cron_ticks[i], cron_ticks[i + 1]) for i in range(len(cron_ticks) - 1)
        ]

        if len(zipped_tick_strs) > 10:
            zipped_tick_strs = zipped_tick_strs[:2] + ["<..>"] + zipped_tick_strs[-2:]

        return zipped_tick_strs
