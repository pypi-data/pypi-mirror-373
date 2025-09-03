from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    VerticaSource as ProtoVerticaSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource


@dataclass
class VerticaSource(BaseBatchSource):
    host: str
    port: int
    database: str
    schema: str
    table: str
    username_secret_name: str
    password_secret_name: str
    repository: Optional[str] = None

    @classmethod
    def _from_proto(cls, proto):
        vertica = proto.verticaSource
        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            host=vertica.host,
            username_secret_name=vertica.username_secret_name,
            password_secret_name=vertica.password_secret_name,
            database=vertica.database,
            schema=vertica.schema,
            port=vertica.port,
            table=vertica.table,
        )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoDataSourceSpec:
        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                verticaSource=ProtoVerticaSource(
                    host=self.host,
                    username_secret_name=self.username_secret_name,
                    password_secret_name=self.password_secret_name,
                    database=self.database,
                    schema=self.schema,
                    port=self.port,
                    table=self.table,
                ),
            ),
        )
