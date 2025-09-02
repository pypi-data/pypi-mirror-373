import functools
import inspect
from dataclasses import dataclass
from datetime import datetime
from inspect import Signature
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

from frogml.feature_store._common.artifact_utils import (
    ArtifactSpec,
    ArtifactsUploader,
)
from frogml.feature_store._common.feature_set_utils import (
    get_batch_source_for_featureset,
)
from frogml.core.feature_store.feature_sets._utils._featureset_utils import (
    FeaturesetUtils,
)
from frogml.feature_store.feature_sets.base_feature_set import BaseFeatureSet
from frogml.core.feature_store.validations.validation_options import (
    FeatureSetValidationOptions,
)

if TYPE_CHECKING:
    try:
        import pandas as pd
    except ImportError:
        pass

from typeguard import typechecked

from frogml._proto.qwak.feature_store.features.execution_pb2 import (
    ExecutionSpec as ProtoExecutionSpec,
)
from frogml._proto.qwak.feature_store.features.feature_set_pb2 import FeatureSetSpec
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    BatchFeatureSetV1 as ProtoBatchFeatureSetV1,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    FeatureSetBatchSource as ProtoFeatureSetBatchSource,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    FeatureSetType as ProtoFeatureSetType,
)
from frogml.core.feature_store.entities.entity import Entity
from frogml.core.feature_store.feature_sets.backfill import Backfill
from frogml.core.feature_store.feature_sets.context import Context
from frogml.core.feature_store.feature_sets.execution_spec import ClusterTemplate
from frogml.core.feature_store.feature_sets.metadata import (
    Metadata,
    get_metadata_from_function,
    set_metadata_on_function,
)
from frogml.core.feature_store.feature_sets.read_policies import (
    ReadPolicy,
    ReadPolicyABC,
)
from frogml.core.feature_store.feature_sets.transformations import BaseTransformation

# decorator attributes
_BACKFILL_POLICY_ATTRIBUTE = "_qwak_backfill_policy"
_EXECUTION_SPECIFICATION_ATTRIBUTE = "_qwak_execution_specification"
_SCHEDULING_POLICY_ATTRIBUTE = "_qwak_scheduling_policy"

# Default timestamp column name for TimeFrame
_DEFAULT_TIMEFRAME_TS_COL_NAME = "qwak_window_end_ts"


def feature_set(
    *,
    data_sources: Union[Dict[str, ReadPolicyABC], List[str]],
    timestamp_column_name: str = None,
    name: str = None,
    entity: Optional[str] = None,
    key: Optional[str] = None,
    repository: Optional[str] = None,
):
    """
    Define a batch scheduled feature set. Default scheduling policy is every 4 hours.

    :param name: The name of the feature set. If not defined, taken from the function name
    :param entity: a string reference to a Frogml entity, or the entity definition itself.
                  Only one of, entity or key, can be provided.
    :param key: a column name in the feature set which is the key. Only one of, entity or key, can be provided.
    :param data_sources: a string reference to a Frogml data source, or the data source definition itself
    :param timestamp_column_name: Timestamp column the feature set should consider when ingesting records.
    If more than one data source is specified - the field is mandatory. If only one data source is specified - the
    field will be taken by from the data source definition.

    Example:

    ... code-block:: python
        @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
        def user_features():
            return SparkSqlTransformation("SELECT user_id, age FROM data_source")

    Example with key:

    ... code-block:: python
    @batch.feature_set(key="user_id", data_sources=["snowflake_users_table"])
    def user_features():
        return SparkSqlTransformation("SELECT user_id, age FROM data_source")
    """

    def decorator(function):
        sig: Signature = inspect.signature(function)
        if "context" in sig.parameters:
            user_transformation = function(context=Context())
        else:
            user_transformation = function()

        FeaturesetUtils.validate_base_featureset_decorator(
            user_transformation=user_transformation, entity=entity, key=key
        )

        fs_name = name or function.__name__
        batch_feature_set = BatchFeatureSet(
            name=fs_name,
            entity=entity if entity else None,
            key=key if key else None,
            repository=repository if repository else None,
            data_sources=data_sources,
            timestamp_column_name=timestamp_column_name,
            transformation=user_transformation,
            scheduling_policy=getattr(
                function, _SCHEDULING_POLICY_ATTRIBUTE, "0 */4 * * *"
            ),
            metadata=get_metadata_from_function(
                function, description=fs_name, display_name=fs_name
            ),
            cluster_template=getattr(
                function,
                _EXECUTION_SPECIFICATION_ATTRIBUTE,
                ClusterTemplate.MEDIUM,
            ),
            backfill=getattr(function, _BACKFILL_POLICY_ATTRIBUTE, None),
            __instance_module_path__=inspect.stack()[1].filename,
        )

        functools.update_wrapper(batch_feature_set, user_transformation)
        return batch_feature_set

    return decorator


@typechecked
def scheduling(*, cron_expression: Optional[str]):
    """
    Sets the scheduling policy of the batch feature set according to the given cron expression
    A cron expression is a string consisting of six or seven subexpressions (fields) that describe individual details
    of the schedule. These fields, separated by white space, can contain any of the allowed values with various
    combinations of the allowed characters for that field.

    If None was passed instead of cron expression, the feature set will not be scheduled,
    and would be triggered only by user request

    Some more examples:

    Expression	Means
    0 0 12 * * ?	Fire at 12:00 PM (noon) every day
    0 15 10 ? * *	Fire at 10:15 AM every day
    0 15 10 * * ?	Fire at 10:15 AM every day
    0 15 10 * * ? *	Fire at 10:15 AM every day
    0 15 10 * * ? 2005	Fire at 10:15 AM every day during the year 2005
    0 * 14 * * ?	Fire every minute starting at 2:00 PM and ending at 2:59 PM, every day

    :param cron_expression: cron expression

    Example:

    ... code-block:: python

        @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
        @batch.scheduling(cron_expression="0 8 * * *")
        def user_features():
            return SparkSqlTransformation("SELECT user_id, age FROM data_source")

    """

    # TODO: add backend validation on cron expression
    def decorator(user_transformation):
        _validate_decorator_ordering(user_transformation)
        setattr(user_transformation, _SCHEDULING_POLICY_ATTRIBUTE, cron_expression)

        return user_transformation

    return decorator


@typechecked
def metadata(
    *,
    owner: Optional[str] = None,
    description: Optional[str] = None,
    display_name: Optional[str] = None,
    version_comment: Optional[str] = None,
):
    """
    Sets additional user provided metadata

    :param owner: feature set owner
    :param description: General description of the feature set
    :param display_name: Human readable name of the feature set
    :param version_comment: Comment which describes the version
    Example:

    ... code-block:: python

        @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
        @batch.metadata(
            owner="datainfra@frogml.com",
            display_name="User Batch Features",
            description="Users feature from the Snowflake replica of the production users table",
        )
        def user_features():
            return SparkSqlTransformation("SELECT user_id, age FROM data_source")

    """

    def decorator(user_transformation):
        _validate_decorator_ordering(user_transformation)
        set_metadata_on_function(
            function=user_transformation,
            owner=owner,
            description=description,
            display_name=display_name,
            version_comment=version_comment,
        )

        return user_transformation

    return decorator


@typechecked
def backfill(
    *,
    start_date: datetime,
):
    """
    Set the backfill policy of the feature set.

    :param start_date: Start date of the backfill process. Data is extracted starting from this date
    :param end_date: Optionally the end date of the backfill process. Cuts off the backfill according to this date

    Example:

    ... code-block:: python
        @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
        @batch.backfill(start_date=datetime(2022, 1, 1))
        def user_features():
            return SparkSqlTransformation("SELECT user_id, age FROM data_source")

    """

    def decorator(user_transformation):
        _validate_decorator_ordering(user_transformation)
        setattr(
            user_transformation,
            _BACKFILL_POLICY_ATTRIBUTE,
            Backfill(start_date=start_date),
        )

        return user_transformation

    return decorator


@typechecked
def execution_specification(
    *,
    cluster_template: ClusterTemplate,
):
    """
    Set the execution specification of the cluster running the feature set

    :param cluster_template: Predefined template sizes

    Cluster template example:

    ... code-block:: python
        @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
        @batch.execution_specification(cluster_template=ClusterTemplate.MEDIUM)
        def user_features():
            return SparkSqlTransformation("SELECT user_id, age FROM data_source"

    """

    def decorator(user_transformation):
        _validate_decorator_ordering(user_transformation)
        setattr(
            user_transformation, _EXECUTION_SPECIFICATION_ATTRIBUTE, cluster_template
        )

        return user_transformation

    return decorator


def _validate_decorator_ordering(user_transformation):
    if isinstance(user_transformation, BatchFeatureSet):
        raise ValueError(
            "Wrong decorator ordering - @batch.feature_set should be the top most decorator"
        )


@dataclass
class BatchFeatureSet(BaseFeatureSet):
    timestamp_column_name: str = str()
    scheduling_policy: str = str()
    transformation: Optional[BaseTransformation] = None
    metadata: Optional[Metadata] = None
    cluster_template: Optional[ClusterTemplate] = None
    backfill: Optional[Backfill] = None

    def __post_init__(self):
        self._validate()

    @classmethod
    def _from_proto(cls, proto: FeatureSetSpec):
        batch_v1_def = proto.feature_set_type.batch_feature_set_v1

        return cls(
            name=proto.name,
            entity=Entity._from_proto(proto.entity),
            data_sources=[
                ds.data_source.name for ds in batch_v1_def.feature_set_batch_sources
            ],
            repository=proto.featureset_repository_name,
            timestamp_column_name=batch_v1_def.timestamp_column_name,
            scheduling_policy=batch_v1_def.scheduling_policy,
            transformation=BaseTransformation._from_proto(batch_v1_def.transformation),
            metadata=Metadata.from_proto(proto.metadata),
            cluster_template=ClusterTemplate.from_cluster_template_number(
                batch_v1_def.execution_spec.cluster_template
            ),
            backfill=Backfill.from_proto(batch_v1_def.backfill),
        )

    def _get_data_sources(self, feature_registry) -> List[ProtoFeatureSetBatchSource]:
        if isinstance(self.data_sources, list):
            actual_data_sources = {
                ds_name: ReadPolicy.NewOnly for ds_name in self.data_sources
            }
        else:
            actual_data_sources = self.data_sources

        return [
            ProtoFeatureSetBatchSource(
                data_source=get_batch_source_for_featureset(ds, feature_registry),
                read_policy=(
                    read_policy().to_proto()
                    if inspect.isclass(read_policy)
                    else read_policy.to_proto()
                ),
            )
            for ds, read_policy in actual_data_sources.items()
        ]

    def _get_timestamp_column(
        self, data_sources: List[ProtoFeatureSetBatchSource]
    ) -> str:
        if self.timestamp_column_name:
            return self.timestamp_column_name

        # if no explicit timestamp column was set AND there's a TimeFrame
        # datasource, set the default column name.
        has_timeframe: bool = any(
            [ds.read_policy.WhichOneof("type") == "time_frame" for ds in data_sources]
        )
        if has_timeframe:
            return _DEFAULT_TIMEFRAME_TS_COL_NAME

        if len(data_sources) >= 2:
            raise ValueError(
                "If more than one data source is defined - `timestamp_column_name` on the feature set decorator must be defined"
            )

        # if we got here - only one data source is defined
        return data_sources[0].data_source.date_created_column

    def _validate(self):
        super()._validate()

    def _to_proto(
        self,
        git_commit,
        features,
        feature_registry,
        artifact_url: Optional[str] = str(),
        **kwargs,
    ) -> Tuple[FeatureSetSpec, Optional[str]]:
        self._validate()

        data_sources = self._get_data_sources(feature_registry)

        if not artifact_url:
            artifact: Optional[ArtifactSpec] = ArtifactsUploader.get_artifact_spec(
                self.transformation, self.name, self.__instance_module_path__
            )
            if artifact:
                artifact_url = ArtifactsUploader.upload(artifact)

        return (
            FeatureSetSpec(
                name=self.name,
                metadata=self.metadata.to_proto(),
                git_commit=git_commit,
                features=features,
                entity=self._get_entity_definition(feature_registry),
                featureset_repository_name=self.repository,
                feature_set_type=ProtoFeatureSetType(
                    batch_feature_set_v1=ProtoBatchFeatureSetV1(
                        online_sink=True,
                        offline_sink=True,
                        timestamp_column_name=self._get_timestamp_column(data_sources),
                        scheduling_policy=self.scheduling_policy,
                        feature_set_batch_sources=data_sources,
                        execution_spec=ProtoExecutionSpec(
                            cluster_template=(
                                ClusterTemplate.to_proto(self.cluster_template)
                                if self.cluster_template
                                else None
                            )
                        ),
                        transformation=(
                            self.transformation._to_proto(artifact_path=artifact_url)
                            if self.transformation
                            else None
                        ),
                        backfill=self.backfill.to_proto() if self.backfill else None,
                    )
                ),
            ),
            artifact_url,
        )

    def get_sample(
        self,
        number_of_rows: int = 10,
        validation_options: Optional[FeatureSetValidationOptions] = None,
    ) -> "pd.DataFrame":
        """
        Fetches a sample of the Feature set transformation by loading requested sample of data from the data source
        and executing the transformation on that data.

        :param number_of_rows: number of rows requests
        :param validation_options: validation options
        :returns Sample Pandas Dataframe

        Example with entity:

        ... code-block:: python
            @batch.feature_set(entity="users", data_sources=["snowflake_users_table"])
            @batch.backfill(start_date=datetime(2022, 1, 1))
            def user_features():
                return SparkSqlTransformation("SELECT user_id, age FROM data_source")

            sample_features = user_features.get_sample()
            print(sample_feature)
            #	    user_id	         timestamp	        user_features.age
            # 0	      1	        2021-01-02 17:00:00	              23
            # 1	      1	        2021-01-01 12:00:00	              51
            # 2	      2	        2021-01-02 12:00:00	              66
            # 3	      2	        2021-01-01 18:00:00	              34

        Example with key:

        ... code-block:: python
            @batch.feature_set(key="user_id", data_sources=["snowflake_users_table"])
            @batch.backfill(start_date=datetime(2022, 1, 1))
            def user_features():
                return SparkSqlTransformation("SELECT user_id, age FROM data_source")

            sample_features = user_features.get_sample()
            print(sample_feature)
            #	    user_id	         timestamp	        user_features.age
            # 0	      1	        2021-01-02 17:00:00	              23
            # 1	      1	        2021-01-01 12:00:00	              51
            # 2	      2	        2021-01-02 12:00:00	              66
            # 3	      2	        2021-01-01 18:00:00	              34
        """
        return super().get_sample(
            number_of_rows=number_of_rows, validation_options=validation_options
        )
