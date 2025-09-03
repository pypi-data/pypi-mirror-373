from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    ClickhouseSource as ProtoClickhouseSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.core.exceptions import FrogmlException
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource


@dataclass
class ClickhouseSource(BaseBatchSource):
    username_secret_name: Optional[str] = None
    password_secret_name: Optional[str] = None
    url: Optional[str] = None
    db_table: Optional[str] = None
    query: Optional[str] = None
    repository: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not (bool(self.db_table) ^ bool(self.query)):
            raise FrogmlException("Only one of query and db_table must be set")

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoDataSourceSpec:
        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                clickhouseSource=ProtoClickhouseSource(
                    url=self.url,
                    username_secret_name=self.username_secret_name,
                    password_secret_name=self.password_secret_name,
                    table=self.db_table,
                    sql=self.query,
                ),
            ),
        )

    @classmethod
    def _from_proto(cls, proto: ProtoBatchSource):
        clickhouse: ProtoClickhouseSource = proto.clickhouseSource
        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            url=clickhouse.url,
            username_secret_name=clickhouse.username_secret_name,
            password_secret_name=clickhouse.password_secret_name,
            db_table=clickhouse.table,
            query=clickhouse.sql,
        )
