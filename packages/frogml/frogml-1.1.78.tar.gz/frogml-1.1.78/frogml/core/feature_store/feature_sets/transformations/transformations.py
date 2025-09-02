import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple
from warnings import warn

if TYPE_CHECKING:
    import pyspark.pandas as psd
    import pyspark.sql as psql

import importlib

from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    AggregationField as ProtoAggregationField,
)
from frogml._proto.qwak.feature_store.features.aggregation_pb2 import (
    TimeWindow as ProtoTimeWindow,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    KoalasTransformation as ProtoKoalasTransformation,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    PandasOnSparkTransformation as ProtoPandasOnSparkTransformation,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    PySparkTransformation as ProtoPySparkTransformation,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    SqlTransformation as ProtoSqlTransformation,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    TransformArguments as ProtoTransformArguments,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    Transformation as ProtoTransformation,
)
from frogml._proto.qwak.feature_store.features.feature_set_types_pb2 import (
    UdfTransformation as ProtoUdfTransformation,
)
from frogml.core.exceptions import FrogmlException
from frogml.core.feature_store._common.value import (
    UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG,
    missing_pyspark_exception_message,
)
from frogml.core.feature_store.feature_sets.transformations.aggregations.aggregations import (
    BaseAggregate,
    FrogmlAggregation,
)
from frogml.core.feature_store.feature_sets.transformations.aggregations.windows import (
    Window,
)
from frogml.core.feature_store.feature_sets.transformations.validations.validations_util import (
    validate_function,
    validate_qwargs,
)
from frogml.core.tools.logger import logger as frogml_logger

logger = frogml_logger.get_frogml_logger()


@dataclass
class BaseTransformation(ABC):
    """
    Base class for Frogml transformations.

    Windows and aggregates are supported only for streaming aggregation featuresets.
    """

    windows: List[Window] = field(init=False, default_factory=list)
    aggregations: Tuple[BaseAggregate] = field(init=False, default_factory=tuple)
    _artifact_path: Optional[str] = field(init=False, default=None)

    def aggregate(self, *aggregations: FrogmlAggregation):
        self.aggregations += aggregations
        return self

    def by_windows(self, *time_windows: str):
        self.windows += Window._from_string(*set(time_windows))
        return self

    def get_names(self) -> List[str]:
        return [a.get_name() for a in self.aggregations]

    def get_features_names(self) -> List[str]:
        if self.windows and self.aggregations:
            return [
                f"{name}_{tu.get_feature_suffix()}"
                for tu in self.windows
                for name in self.get_names()
            ]
        else:
            raise FrogmlException(
                "Feature names are retrieved for streaming aggregation featuresets only"
            )

    def _get_aggregations_proto(self) -> List[ProtoAggregationField]:
        """
        Converts a user-defined streaming aggregation transformation to a list of proto aggregation fields
        Time windows are applied to all defined aggregations (cartesian product)
        """

        time_windows: List[ProtoTimeWindow] = [
            ProtoTimeWindow(length=window.length, time_unit=window.time_unit_proto)
            for window in self.windows
        ]

        proto_aggregations: List[ProtoAggregationField] = []

        for aggregation in self.aggregations:
            aggregation_params = {
                aggregation._key: aggregation.to_proto(),
                "time_windows": time_windows,
            }
            if aggregation.has_alias():
                aggregation_params["field_name_prefix"] = aggregation._alias_name

            proto_aggregations.append(ProtoAggregationField(**aggregation_params))

        return proto_aggregations

    @classmethod
    def _from_proto(cls, proto: ProtoTransformation):
        function_mapping = {
            "sql_transformation": SparkSqlTransformation,
            "koalas_transformation": KoalasTransformation,
            "pyspark_transformation": PySparkTransformation,
            "udf_transformation": UdfTransformation,
            "pandas_on_spark_transformation": PandasOnSparkTransformation,
        }

        function_type: str = proto.WhichOneof("type")

        if function_type in function_mapping:
            function_class = function_mapping.get(function_type)
            return function_class._from_proto(proto)

        raise FrogmlException(f"Got unsupported transformation type: {function_type}")

    @abstractmethod
    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        pass

    def get_functions(self) -> Optional[List[Callable]]:
        return None

    def _validate_udfs(self):
        udfs: Optional[List[Callable]] = self.get_functions()

        if udfs and len(udfs) > 0:
            python_major = sys.version_info[0]
            python_minor = sys.version_info[1]
            if f"{python_major}.{python_minor}" != "3.8":
                raise FrogmlException(
                    f"Feature store UDFs are only supported for python 3.8, instead got: "
                    f"{python_major}.{python_minor}"
                )


@dataclass
class KoalasTransformation(BaseTransformation):
    """
    Koalas transformation, providing the user with the ability to define a Koalas based UDF for the transformation
    of the FeatureSet. This option will be deprecated in future versions.
    @param function: The Koalas function defined for the transformation
    @type: Callable
    @deprecated
    """

    function: Optional[Callable] = None
    qwargs: Optional[Dict[str, str]] = None

    def __post_init__(self):
        warn(
            "Koalas transformation is about to be deprecated. "
            "Please use PySparkTransformation, SparkSqlTransformation or UDFTransformation instead",
            DeprecationWarning,
            stacklevel=2,
        )

        self.qwargs = self.qwargs if self.qwargs else {}
        self.qwargs = {str(k): str(v) for k, v in self.qwargs.items()}
        self._artifact_path = None

        if not self.function:
            raise FrogmlException(
                "Please provide a valid function for the koalas transformation"
            )

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            koalas_transformation=ProtoKoalasTransformation(
                function_name=self.function.__name__,
                qwargs=ProtoTransformArguments(qwargs=self.qwargs),
            ),
            artifact_path=self._artifact_path,
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        koalas_transformation = proto.koalas_transformation
        qwargs = {}
        if koalas_transformation.WhichOneof("args_option") == "qwargs":
            qwargs = koalas_transformation.qwargs.qwargs

        def f():
            print(
                f"Loading Koalas UDFs is not supported. Can not load {koalas_transformation.function_name}"
            )

        f.__name__ = koalas_transformation.function_name

        return cls(function=f, qwargs=qwargs)

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]


@dataclass
class PySparkTransformation(BaseTransformation):
    """
    PySpark transformation, providing the user with the ability to define a PySpark based UDF for the transformation
    of the FeatureSet.
    @param function: The PySpark function defined for the transformation
    @type: Callable
    @deprecated
    """

    function: Callable[
        [Dict[str, "psql.DataFrame"], Dict[str, Any]],
        "psql.DataFrame",
    ]
    qwargs: Optional[Dict[str, str]] = None

    def __post_init__(self):
        self.qwargs = self.qwargs if self.qwargs else {}
        self._artifact_path = None

        if importlib.util.find_spec("pyspark"):
            import pyspark

            validate_function(self.function, pyspark.sql.DataFrame, self.__class__)
        else:
            raise FrogmlException(
                missing_pyspark_exception_message(self.__class__.__name__)
            )

        validate_qwargs(self.qwargs)

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            pyspark_transformation=ProtoPySparkTransformation(
                function_name=self.function.__name__,
                qwargs=ProtoTransformArguments(qwargs=self.qwargs),
            ),
            artifact_path=self._artifact_path,
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        try:
            import pyspark.sql as ps
        except Exception:
            raise FrogmlException(missing_pyspark_exception_message(cls.__name__))

        pyspark_transformation = proto.pyspark_transformation
        qwargs = {}
        if pyspark_transformation.WhichOneof("args_option") == "qwargs":
            qwargs = pyspark_transformation.qwargs.qwargs

        def f(dfs: Dict[str, ps.DataFrame]) -> ps.DataFrame:
            print(
                f"Loading Pyspark UDFs is not supported. Can not load {pyspark_transformation.function_name}"
            )

        f.__name__ = pyspark_transformation.function_name

        return cls(function=f, qwargs=qwargs)

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]


@dataclass
class SparkSqlTransformation(BaseTransformation):
    """
    A Spark SQL transformation
    :param sql: A valid Spark SQL transformation
    :param functions: PySpark Pandas UDFs
    Example transformation:
    ... code-block:: python
        SparkSqlTransformation("SELECT user_id, age FROM data_source")
    Example transformation with additional UDFs:
    ... code-block:: python
        @frogml_pandas_udf(output_schema=Schema([
            Column(type=Type.long)]))
        def plus_one(column_a: pd.Series) -> pd.Series:
            return column_a + 1


        @frogml_pandas_udf(output_schema=Schema([
            Column(type=Type.long)]))
        def mul_by_two(column_a: pd.Series) -> pd.Series:
            return column_a * 2

        SparkSqlTransformation("SELECT user_id, age FROM data_source", functions=[plus_one, mul_by_two])
    """

    sql: str = str()
    functions: Optional[List[Callable]] = None

    def __post_init__(self):
        if not self.sql:
            raise FrogmlException(
                "SQL statement can not be empty when using a SparkSqlTransformation"
            )

    @classmethod
    def _from_proto(cls, proto: "ProtoSqlTransformation"):
        return cls(sql=proto.sql_transformation.sql)

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        return ProtoTransformation(
            sql_transformation=ProtoSqlTransformation(
                sql=self.sql,
                function_names=(
                    [function.__name__ for function in self.functions]
                    if self.functions
                    else None
                ),
            ),
            artifact_path=artifact_path,
        )

    def get_functions(self) -> Optional[List[Callable]]:
        return self.functions


@dataclass
class UdfTransformation(BaseTransformation):
    """
    A UDF Transformation
    :param function: A valid user defined pandas function decorated with the @frogml_pandas_udf decorator
    Example transformation:
    ... code-block:: python

    @frogml_pandas_udf(output_schema=Schema([Column(type=Type.long)]))
    def my_pandas_udf() -> pd.Series:
        data = np.random.randn(3)
        series = pd.Series(data)
        return series

    UdfTransformation(function=my_pandas_udf)
    """

    function: Callable = ()

    def __post_init__(self):
        if not self.function:
            raise FrogmlException("Please provide a function to the UdfTransformation")

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            artifact_path=artifact_path,
            udf_transformation=ProtoUdfTransformation(
                function_name=self.function.__name__
            ),
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        return cls(
            function=lambda x: print("Loading UDFs is not yet supported"),
        )

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]


@dataclass
class PandasOnSparkTransformation(BaseTransformation):
    """
    Pandas On Spark transformation.
    This class provides the user with the ability to define a Pandas On Spark based UDF as the transformation of the Feature Set.

    Attributes
    ----------
    function : Callable
        The Pandas On Spark function defined for the transformation.
    qwargs : dict, optional
        Runtime parameters (e.g., frogml_ingestion_start_timestamp, frogml_ingestion_end_timestamp).
    """

    function: Callable[
        [Dict[str, "psd.DataFrame"], Dict[str, Any]],
        "psd.DataFrame",
    ]
    qwargs: Optional[Dict[str, str]] = None

    def __post_init__(self):
        self.qwargs = self.qwargs if self.qwargs else {}
        self._artifact_path = None
        if importlib.util.find_spec("pyspark"):
            import pyspark.pandas as psd

            validate_function(self.function, psd.DataFrame, self.__class__)
        else:
            raise FrogmlException(
                missing_pyspark_exception_message(self.__class__.__name__)
            )
        validate_qwargs(self.qwargs)

    def _to_proto(self, artifact_path: Optional[str] = None) -> ProtoTransformation:
        self._validate_udfs()

        if artifact_path:
            self._artifact_path = artifact_path

        return ProtoTransformation(
            pandas_on_spark_transformation=ProtoPandasOnSparkTransformation(
                function_name=self.function.__name__,
                qwargs=ProtoTransformArguments(qwargs=self.qwargs),
            ),
            artifact_path=self._artifact_path,
        )

    @classmethod
    def _from_proto(cls, proto: "ProtoTransformation"):
        try:
            import pyspark.pandas as ps
        except Exception:
            raise FrogmlException(
                "Missing 'pyspark' dependency required for PandasOnSpark transformation. "
                f"{UPDATE_FROGML_SDK_WITH_FEATURE_STORE_EXTRA_MSG}"
            )
        pandas_on_spark_transformation = proto.pandas_on_spark_transformation
        qwargs = {}
        if pandas_on_spark_transformation.WhichOneof("args_option") == "qwargs":
            qwargs = pandas_on_spark_transformation.qwargs.qwargs

        def f(dfs: Dict[str, ps.DataFrame]) -> ps.DataFrame:
            print(
                f"Loading Pandas On Spark UDFs is not supported. Can not load {pandas_on_spark_transformation.function_name}"
            )

        f.__name__ = pandas_on_spark_transformation.function_name

        return cls(function=f, qwargs=qwargs)

    def get_functions(self) -> Optional[List[Callable]]:
        return [self.function]
