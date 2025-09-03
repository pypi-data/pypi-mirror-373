from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from google.protobuf.timestamp_pb2 import Timestamp as ProtoTimestamp

from frogml._proto.qwak.features_operator.v3.features_operator_async_service_pb2 import (
    DataSourceValidationOptions as ProtoDataSourceValidationOptions,
)
from frogml._proto.qwak.features_operator.v3.features_operator_async_service_pb2 import (
    FeatureSetValidationOptions as ProtoFeatureSetValidationOptions,
)
from frogml._proto.qwak.features_operator.v3.features_operator_async_service_pb2 import (
    ValidationTimeRange as ProtoValidationTimeRange,
)
from frogml.core.utils.datetime_utils import datetime_to_pts


@dataclass
class ValidationTimeRange:
    lower_time_bound: Optional[datetime] = None
    upper_time_bound: Optional[datetime] = None

    def to_proto(self) -> ProtoValidationTimeRange:
        lower_time_bound_proto: Optional[ProtoTimestamp] = None
        upper_time_bound_proto: Optional[ProtoTimestamp] = None

        if self.lower_time_bound:
            lower_time_bound_proto = datetime_to_pts(self.lower_time_bound)
        if self.upper_time_bound:
            upper_time_bound_proto = datetime_to_pts(self.upper_time_bound)

        return ProtoValidationTimeRange(
            lower_time_bound=lower_time_bound_proto,
            upper_time_bound=upper_time_bound_proto,
        )


@dataclass
class DataSourceValidationOptions:
    time_range: Optional[ValidationTimeRange] = field(
        default_factory=lambda: ValidationTimeRange()
    )

    def __init__(
        self,
        lower_time_bound: Optional[datetime] = None,
        upper_time_bound: Optional[datetime] = None,
    ):
        self.time_range = ValidationTimeRange(
            lower_time_bound=lower_time_bound, upper_time_bound=upper_time_bound
        )

    def to_proto(self) -> ProtoDataSourceValidationOptions:
        return ProtoDataSourceValidationOptions(
            validation_time_range=self.time_range.to_proto()
        )


@dataclass
class FeatureSetValidationOptions:
    time_range: Optional[ValidationTimeRange] = field(
        default_factory=lambda: ValidationTimeRange()
    )
    data_source_limit: Optional[int] = None

    def __init__(
        self,
        lower_time_bound: Optional[datetime] = None,
        upper_time_bound: Optional[datetime] = None,
        data_source_limit: Optional[int] = None,
    ):
        self.time_range = ValidationTimeRange(
            lower_time_bound=lower_time_bound, upper_time_bound=upper_time_bound
        )
        self.data_source_limit = data_source_limit

    def to_proto(self) -> ProtoFeatureSetValidationOptions:
        return ProtoFeatureSetValidationOptions(
            data_source_limit=self.data_source_limit,
            validation_time_range=self.time_range.to_proto(),
        )
