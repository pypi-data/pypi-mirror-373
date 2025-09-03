from abc import ABC
from dataclasses import dataclass

from frogml._proto.qwak.feature_store.features.aggregation_pb2 import Avg as ProtoAvg
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    BooleanAnd as ProtoBooleanAnd,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    BooleanOr as ProtoBooleanOr,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    Count as ProtoCount,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    LastDistinctN as ProtoLastDistinctN,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    LastN as ProtoLastN,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import Max as ProtoMax
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import Min as ProtoMin
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    Percentile as ProtoPercentile,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    PopulationSTDEV as ProtoPopulationSTDEV,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    PopulationVariance as ProtoPopulationVariance,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    SampleSTDEV as ProtoSampleSTDEV,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    SampleVariance as ProtoSampleVariance,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import Sum as ProtoSum
from frogml.core.exceptions import FrogmlException


@dataclass
class BaseAggregate(ABC):
    """
    Base class for Frogml supported aggregations
    """

    def __init__(self, column):
        self._column: str = column
        self._alias_name: str = ""

        self.__post_init__()

    def __post_init__(self):
        if "." in self._column:
            raise FrogmlException(
                f"Aggregation {self.__repr__()} column {self._column} contains an illegal character '.'"
            )

    @property
    def _key(self):
        raise NotImplementedError

    @property
    def _proto_class(self):
        raise NotImplementedError

    def alias(self, name):
        if "." in name:
            raise FrogmlException(
                f"Aggregation {self.__repr__()} alias {name} contains an illegal character '.'"
            )
        self._alias_name = name
        return self

    def has_alias(self):
        return bool(self._alias_name)

    def to_proto(self):
        return self._proto_class(field_name=self._column)

    def get_name(self):
        return self._alias_name if self.has_alias() else f"{self._key}_{self._column}"


class SumAggregate(BaseAggregate):
    _key = "sum"
    _proto_class = ProtoSum


class CountAggregate(BaseAggregate):
    _key = "count"
    _proto_class = ProtoCount


class MaxAggregate(BaseAggregate):
    _key = "max"
    _proto_class = ProtoMax


class MinAggregate(BaseAggregate):
    _key = "min"
    _proto_class = ProtoMin


class AvgAggregate(BaseAggregate):
    _key = "avg"
    _proto_class = ProtoAvg


class SampleVarianceAggregate(BaseAggregate):
    _key = "sample_variance"
    _proto_class = ProtoSampleVariance


class PopulationVarianceAggregate(BaseAggregate):
    _key = "population_variance"
    _proto_class = ProtoPopulationVariance


class SampleSTDEVAggregate(BaseAggregate):
    _key = "sample_stdev"
    _proto_class = ProtoSampleSTDEV


class PopulationSTDEVAggregate(BaseAggregate):
    _key = "population_stdev"
    _proto_class = ProtoPopulationSTDEV


class BooleanAndAggregate(BaseAggregate):
    _key = "boolean_and"
    _proto_class = ProtoBooleanAnd


class BooleanOrAggregate(BaseAggregate):
    _key = "boolean_or"
    _proto_class = ProtoBooleanOr


class LastNAggregate(BaseAggregate):
    _key = "last_n"
    _proto_class = ProtoLastN

    def __init__(self, column: str, n: int):
        self.n = n
        super().__init__(column)
        self.__post_init__()

    def __post_init__(self):
        self._validate()
        super().__post_init__()

    def _validate(self):
        if not (type(self.n) is int and self.n > 0):
            raise FrogmlException("p must be a positive integer")

    def to_proto(self):
        return self._proto_class(field_name=self._column, n=self.n)

    def get_name(self):
        return self._alias_name if self.has_alias() else f"last_{self.n}_{self._column}"


class LastDistinctNAggregate(BaseAggregate):
    _key = "last_distinct_n"
    _proto_class = ProtoLastDistinctN

    def __init__(self, column: str, n: int):
        self.n = n
        super().__init__(column)
        self.__post_init__()

    def __post_init__(self):
        self._validate()
        super().__post_init__()

    def _validate(self):
        if not (type(self.n) is int and self.n > 0):
            raise FrogmlException("p must be a positive integer")

    def to_proto(self):
        return self._proto_class(field_name=self._column, n=self.n)

    def get_name(self):
        return (
            self._alias_name
            if self.has_alias()
            else f"last_distinct_{self.n}_{self._column}"
        )


class PercentileAggregate(BaseAggregate):
    _key = "percentile"
    _proto_class = ProtoPercentile

    def __init__(self, column: str, p: int):
        self.p = p
        super().__init__(column)
        self.__post_init__()

    def __post_init__(self):
        self._validate()
        super().__post_init__()

    def _validate(self):
        if not (type(self.p) is int and 0 < self.p < 100):
            raise FrogmlException("p must be an integer between 1 and 99")

    def to_proto(self):
        return self._proto_class(field_name=self._column, p=self.p)

    def get_name(self):
        return self._alias_name if self.has_alias() else f"p{self.p}_{self._column}"


class FrogmlAggregation:
    """
    Holding all Frogml native supported aggregations. Currently, can be used in Streaming feature sets only.
    """

    @staticmethod
    def sum(column):
        """
        A sum aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.sum("amount"))\
        >>>     .by_windows("1 day"),
        """
        return SumAggregate(column)

    @staticmethod
    def count(column):
        """
        A count aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.count("amount"))\
        >>>     .by_windows("1 day"),
        """
        return CountAggregate(column)

    @staticmethod
    def max(column):
        """
        A max aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.max("amount"))\
        >>>     .by_windows("1 day"),
        """
        return MaxAggregate(column)

    @staticmethod
    def min(column):
        """
        A min aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.min("amount"))\
        >>>     .by_windows("1 day"),
        """
        return MinAggregate(column)

    @staticmethod
    def avg(column):
        """
        A avarage aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.avg("amount"))\
        >>>     .by_windows("1 day"),
        """
        return AvgAggregate(column)

    @staticmethod
    def sample_variance(column):
        """
        A sample variance aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.sample_variance("amount"))\
        >>>     .by_windows("1 day"),
        """
        return SampleVarianceAggregate(column)

    @staticmethod
    def population_variance(column):
        """
        A population variance aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.population_variance("amount"))\
        >>>     .by_windows("1 day"),
        """
        return PopulationVarianceAggregate(column)

    @staticmethod
    def sample_stdev(column):
        """
        A sample STDEV aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.sample_stdev("amount"))\
        >>>     .by_windows("1 day"),
        """
        return SampleSTDEVAggregate(column)

    @staticmethod
    def population_stdev(column):
        """
        A population STDEV aggregation

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.population_stdev("amount"))\
        >>>     .by_windows("1 day"),
        """
        return PopulationSTDEVAggregate(column)

    @staticmethod
    def boolean_and(column):
        """
        A BOOLEAN AND aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.boolean_and("is_fraud"))\
        >>>     .by_windows("1 day"),
        """
        return BooleanAndAggregate(column)

    @staticmethod
    def boolean_or(column):
        """
        A BOOLEAN OR aggregation.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.boolean_or("is_fraud"))\
        >>>     .by_windows("1 day"),
        """
        return BooleanOrAggregate(column)

    @staticmethod
    def last_n(column, n):
        """
        A last_n aggregation

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.last_n("amount", n=10))\
        >>>     .by_windows("1 day"),
        """
        return LastNAggregate(column, n=n)

    @staticmethod
    def last_distinct_n(column, n):
        """
        A last_distinct_n aggregation

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.last_distinct_n("amount", n=10))\
        >>>     .by_windows("1 day"),
        """
        return LastDistinctNAggregate(column, n=n)

    @staticmethod
    def percentile(column, p):
        """
        Calculates a percentile - e.g., p50 (aka median), p90 etc.

        Example:
        >>> from frogml.core import SparkSqlTransformation
        >>> from frogml.core import FrogmlAggregation
        >>>
        >>> SparkSqlTransformation(sql="SELECT id, amount, event_timestamp, offset" \
        >>>                                      "topic, partition FROM transaction_stream")\
        >>>     .aggregate(FrogmlAggregation.percentile("amount", p=50).alias("median_amount"))\
        >>>     .by_windows("1 day"),
        """
        return PercentileAggregate(column, p=p)
