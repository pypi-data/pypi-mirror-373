from typing import Any, Optional

from frogml.core.exceptions import FrogmlException
from frogml.core.feature_store.feature_sets.transformations import BaseTransformation


class FeaturesetUtils:
    @staticmethod
    def validate_base_featureset_decorator(
        user_transformation: Any,
        entity: Optional[str] = None,
        key: Optional[str] = None,
    ):
        if not isinstance(user_transformation, BaseTransformation):
            raise ValueError(
                "Function must return a valid frogml transformation function"
            )
        if (not key) is (not entity):
            raise ValueError(
                "Key and entity are mutually exclusive, please specify only one"
            )

    @staticmethod
    def validate_streaming_featureset_decorator(
        online_trigger_interval: Any, offline_scheduling_policy: Any
    ):
        import croniter

        # verify the cron expression is valid
        if not isinstance(
            offline_scheduling_policy, str
        ) or not croniter.croniter.is_valid(offline_scheduling_policy):
            raise FrogmlException(
                f"Offline scheduling policy provided '{offline_scheduling_policy}' "
                f"is not a valid cron expression"
            )

        # verify the online scheduling policy is valid
        online_interval = online_trigger_interval
        if not (type(online_interval) is int and online_interval >= 0):
            raise FrogmlException(
                f"Value '{online_interval}'"
                f" is not a legal online scheduling policy, "
                f"only non-negative integers are allowed"
            )
