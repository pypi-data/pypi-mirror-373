import pandas as pd
from dateutil.parser import ParserError

from frogml.core.exceptions import FrogmlException
from frogml.core.feature_store.offline.feature_set_features import FeatureSetFeatures


def validate_point_in_time_column_in_population(
    population: "pd.DataFrame", point_in_time_column_name: str
):
    if point_in_time_column_name not in population:
        raise FrogmlException(
            f"The point in time column: `{point_in_time_column_name}` must be part of the population dataframe, current columns: {population.columns}"
        )

    from pandas.api.types import is_datetime64_any_dtype

    if not is_datetime64_any_dtype(population[point_in_time_column_name]):
        try:
            population[point_in_time_column_name] = pd.to_datetime(
                population[point_in_time_column_name]
            )
        except ParserError as e:
            raise FrogmlException(
                f"It was not possible to cast provided point in time column to datetime"
                f"\nError message: {e}"
            )


def validate_features(featureset_features: FeatureSetFeatures):
    if not featureset_features.feature_set_name:
        raise FrogmlException("features.feature_set_name must be set")
