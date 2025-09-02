import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

from google.protobuf.timestamp_pb2 import Timestamp as ProtoTimestamp

from frogml._proto.qwak.offline.serving.v1.feature_values_pb2 import (
    FeaturesetFeatures as ProtoFeaturesetFeatures,
)
from frogml._proto.qwak.offline.serving.v1.offline_serving_async_service_pb2 import (
    FeatureValuesRequestStatus as ProtoFeatureValuesRequestStatus,
)
from frogml._proto.qwak.offline.serving.v1.offline_serving_async_service_pb2 import (
    FileFormat as ProtoFileFormat,
)
from frogml._proto.qwak.offline.serving.v1.offline_serving_async_service_pb2 import (
    GetFeatureValuesResultResponse as ProtoGetFeatureValuesResultResponse,
)
from frogml._proto.qwak.offline.serving.v1.options_pb2 import OfflineServingQueryOptions
from frogml._proto.qwak.offline.serving.v1.options_pb2 import (
    OfflineServingQueryOptions as ProtoOfflineServingQueryOptions,
)
from frogml._proto.qwak.offline.serving.v1.population_pb2 import (
    ArrowSchemaJson as ProtoArrowSchemaJson,
)
from frogml._proto.qwak.offline.serving.v1.population_pb2 import (
    Population as ProtoPopulation,
)
from frogml._proto.qwak.offline.serving.v1.population_pb2 import (
    PopulationFile as ProtoPopulationFile,
)
from frogml._proto.qwak.offline.serving.v1.population_pb2 import (
    TimedPopulation as ProtoTimedPopulation,
)
from frogml.core.clients.feature_store.offline_serving_client import (
    FsOfflineServingClient,
)
from frogml.core.exceptions import FrogmlException
from frogml.feature_store._common.packaging import upload_to_s3
from frogml.core.feature_store._common.value import (
    UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG,
)
from frogml.core.feature_store.offline._offline_serving_validations import (
    validate_features,
    validate_point_in_time_column_in_population,
)
from frogml.core.feature_store.offline.feature_set_features import FeatureSetFeatures
from frogml.core.utils.datetime_utils import datetime_to_pts

try:
    import pandas as pd
except ImportError:
    pass


class OfflineClientV2:
    """
    A class used to retrieve data from the offline store - mainly used to get train data for models.
    It requires frogml configure and aws access.
    """

    POPULATION_CONTENT_TYPE = "application/octet-stream"

    def __init__(self):
        self._fs_offline_serving_client = FsOfflineServingClient()

    def get_feature_range_values(
        self,
        features: FeatureSetFeatures,
        start_date: datetime,
        end_date: datetime,
        population: Optional["pd.DataFrame"] = None,
        include_featureset_version_column: bool = False,
    ) -> "pd.DataFrame":
        """
        :param features: a list of features to fetch
        :param start_date: lower bound of the range to fetch
        :param end_date: upper bound of the range to fetch
        :param population: a pandas data-frame with a column for each entity key of the feature-set defined in `features`
                           argument. if defenind- result will be filtered by the given entity values.
        :param include_featureset_version_column: whether to include featureset version column in resulting dataframe

        :return: a pandas dataframe - all feature values for
         all entites under the given date range

        each row in the returned data-frame is constructed by retrieving the requested features of the entity
         key(s) for all entity values in within the defined date tange.

        Examples:
        >>> from datetime import datetime
        >>> from frogml.core import OfflineClientV2
        >>> from frogml.core import FeatureSetFeatures
        >>>
        >>> start_date = datetime(year=2021, month=1, day=1)
        >>> end_date = datetime(year=2021, month=1, day=3)
        >>> features = FeatureSetFeatures(
        >>>     feature_set_name='user_purchases',
        >>>     feature_names=['number_of_purchases', 'avg_purchase_amount']
        >>> )
        >>> offline_feature_store = OfflineClientV2()
        >>>
        >>> train_df = offline_feature_store.get_feature_range_values(
        >>>                features=features,
        >>>                start_date=start_date,
        >>>                end_date=end_date)
        >>>
        >>> print(train_df.head())
        >>> #	     uuid	         timestamp	      user_purchases.number_of_purchases	user_purchases.avg_purchase_amount
        >>> # 0	      1	        2021-01-02 17:00:00	                 76	                                4.796842
        >>> # 1	      1	        2021-01-01 12:00:00	                 5	                                1.548000
        >>> # 2	      2	        2021-01-02 12:00:00	                 5	                                5.548000
        >>> # 3	      2	        2021-01-01 18:00:00	                 5	                                2.788000
        """
        try:
            import pandas as pd
        except ImportError:
            raise FrogmlException(
                "Missing 'pandas' dependency required for fetching data from the offline store."
                f" {UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            )

        validate_features(features)
        population_proto: Optional[ProtoPopulation] = None
        if population is not None:
            population_proto = self._prepare_and_get_population(population)

        options: OfflineServingQueryOptions = ProtoOfflineServingQueryOptions(
            include_featureset_version_column=include_featureset_version_column
        )

        features_proto: ProtoFeaturesetFeatures = features.to_proto()
        try:
            logging.info("Executing Feature Values in range query")

            lower_time_bound_proto: ProtoTimestamp = datetime_to_pts(start_date)
            upper_time_bound_proto: ProtoTimestamp = datetime_to_pts(end_date)
            response: ProtoGetFeatureValuesResultResponse = (
                self._fs_offline_serving_client.get_feature_values_in_range_blocking(
                    features=features_proto,
                    lower_time_bound=lower_time_bound_proto,
                    upper_time_bound=upper_time_bound_proto,
                    result_file_format=ProtoFileFormat.FILE_FORMAT_CSV,
                    population=population_proto,
                    options=options,
                )
            )

            res: pd.DataFrame = OfflineClientV2._results_response_to_df(response)
            return res
        except FrogmlException as frogml_exception:
            raise FrogmlException(
                f"Got the following Frogml generated exception: {frogml_exception}"
            )
        except Exception as e:
            raise FrogmlException(f"Got the following run-time exception: {e}")

    def get_feature_values(
        self,
        features: List[FeatureSetFeatures],
        population: "pd.DataFrame",
        point_in_time_column_name: str = "timestamp",
        include_featureset_version_column: bool = False,
    ) -> "pd.DataFrame":
        """
        :param features: a list of FeatureSetFeatures to fetch.
        :param population: a pandas data-frame with a point in time column
                           and a column for each entity key of the feature-sets defined in `features`.
        :param point_in_time_column_name: the column name of the point in time column (default - timestamp)
        :param include_featureset_version_column: whether to include featureset version column in resulting dataframe

        :return: a pandas data-frame - the population joined with the feature values for all
                                       the requested entities and features.

        each row in the returned data-frame is constructed by retrieving the requested features of the entity key(s) for
        the specific entity value(s) in the population and on the specific point in time defined.

        Feature sets should be named [Feature Set Name].[Feature Name],
        i.e: user_purchases.number_of_purchases.

        Examples:
        >>> import pandas as pd
        >>> from frogml.core import OfflineClientV2
        >>> from frogml.core import FeatureSetFeatures
        >>>
        >>> population_df = pd.DataFrame(
        >>>     columns= ['uuid',       'timestamp'     ],
        >>>     data   =[[ '1'  , '2021-01-02 17:00:00' ],
        >>>              [ '2'  , '2021-01-01 12:00:00' ]])
        >>>
        >>> features = [
        >>>     FeatureSetFeatures(feature_set_name='user_purchases',
        >>>                        feature_names=['number_of_purchases', 'avg_purchase_amount']),
        >>> ]
        >>> offline_feature_store = OfflineClientV2()
        >>>
        >>> train_df = offline_feature_store.get_feature_values(
        >>>                features=features,
        >>>                population=population_df,
        >>>                point_in_time_column_name='timestamp')
        >>>
        >>> print(train_df.head())
        >>> #	     uuid	         timestamp	      user_purchases.number_of_purchases	user_purchases.avg_purchase_amount
        >>> # 0	      1	        2021-04-24 17:00:00	                 76	                                4.796842
        >>> # 1	      2	        2021-04-24 12:00:00	                 5	                                1.548000
        """
        try:
            import pandas as pd
        except ImportError:
            raise FrogmlException(
                "Missing 'pandas' dependency required for fetching data from the offline store."
                f" {UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            )

        [validate_features(feature) for feature in features]
        validate_point_in_time_column_in_population(
            population=population, point_in_time_column_name=point_in_time_column_name
        )
        population_proto: ProtoPopulation = self._prepare_and_get_population(population)
        timed_population_proto: ProtoTimedPopulation = ProtoTimedPopulation(
            timestamp_column_name=point_in_time_column_name, population=population_proto
        )
        options: OfflineServingQueryOptions = ProtoOfflineServingQueryOptions(
            include_featureset_version_column=include_featureset_version_column
        )

        features_proto: List[ProtoFeaturesetFeatures] = [f.to_proto() for f in features]
        try:
            logging.info("Executing Feature Values query")
            response: ProtoGetFeatureValuesResultResponse = (
                self._fs_offline_serving_client.get_feature_values_blocking(
                    features=features_proto,
                    result_file_format=ProtoFileFormat.FILE_FORMAT_CSV,
                    population=timed_population_proto,
                    options=options,
                )
            )

            res: pd.DataFrame = OfflineClientV2._results_response_to_df(response)
            return res
        except FrogmlException as frogml_exception:
            raise FrogmlException(
                f"Got the following Frogml generated exception: {frogml_exception}"
            )
        except Exception as e:
            raise FrogmlException(f"Got the following run-time exception: {e}")

    def _prepare_and_get_population(
        self,
        popuation_df: "pd.DataFrame",
    ) -> ProtoPopulation:
        population_arrow_schema_json = OfflineClientV2._pandas_to_json_arrow_schema(
            popuation_df
        )
        population_upload_file_url = (
            self._fs_offline_serving_client.get_population_file_upload_url()
        )
        population_stream = popuation_df.to_parquet(index=False, coerce_timestamps="ms")

        upload_to_s3(
            population_upload_file_url, population_stream, self.POPULATION_CONTENT_TYPE
        )

        return ProtoPopulation(
            population_file=ProtoPopulationFile(
                file_url=population_upload_file_url,
                arrow_schema_json=ProtoArrowSchemaJson(
                    schema=population_arrow_schema_json
                ),
            )
        )

    @staticmethod
    def _pandas_to_json_arrow_schema(popuation_df: "pd.DataFrame") -> str:
        try:
            from pyarrow import DataType, Field, ListType, Schema, StructType
        except ImportError:
            raise FrogmlException(
                f"""
                Missing 'pyarrow' dependency required for fetching data from the offline store.
                {UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            """
            )

        def arrow_field_type_to_json(
            field_type: DataType,
        ) -> Union[Dict[str, str], str]:
            if isinstance(field_type, StructType):
                internal_res = {}
                for i in range(field_type.num_fields):
                    internal_field: Field = field_type.field(i)
                    internal_json_type = arrow_field_type_to_json(internal_field.type)
                    internal_res[internal_field.name] = internal_json_type

                ret_val = {"struct": internal_res}
            elif isinstance(field_type, ListType):
                value_type: DataType = field_type.value_type
                internal_json_type = arrow_field_type_to_json(value_type)
                ret_val = {"list": internal_json_type}
            else:
                ret_val = str(field_type)

            return ret_val

        arrow_schema: Schema = Schema.from_pandas(popuation_df)
        res = {}
        for i in range(len(arrow_schema.types)):
            field: Field = arrow_schema.field(i)
            json_type = arrow_field_type_to_json(field.type)
            res[field.name] = json_type

        return json.dumps(res)

    @staticmethod
    def _results_response_to_df(
        response: ProtoGetFeatureValuesResultResponse,
    ) -> "pd.DataFrame":
        if (
            response.status
            == ProtoFeatureValuesRequestStatus.FEATURE_VALUES_REQUEST_STATUS_SUCCEEDED
        ):
            dfs = [pd.read_csv(f) for f in response.link_to_files.link_to_files]
            return pd.concat(dfs)
        elif (
            response.status
            == ProtoFeatureValuesRequestStatus.FEATURE_VALUES_REQUEST_STATUS_FAILED
        ):
            failure_reason = response.failure_reason.message
            raise FrogmlException(
                f"Failed to get Feature Values with the following error message: {failure_reason}"
            )
        elif (
            response.status
            == ProtoFeatureValuesRequestStatus.FEATURE_VALUES_REQUEST_STATUS_CANCELLED
        ):
            raise FrogmlException(
                "Failed to get Feature Values, request was cancelled by another source"
            )
        else:
            raise FrogmlException("Got an unexpected Feature Values Status")
