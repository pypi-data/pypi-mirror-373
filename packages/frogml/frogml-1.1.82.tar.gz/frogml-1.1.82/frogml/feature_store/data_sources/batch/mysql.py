from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    JdbcSource as ProtoJdbcSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    MysqlSource as ProtoMysqlSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.feature_store.data_sources.batch._jdbc import JdbcSource


@dataclass
class MysqlSource(JdbcSource):
    @classmethod
    def _from_proto(cls, proto):
        mysql = proto.jdbcSource
        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            url=mysql.url,
            username_secret_name=mysql.username_secret_name,
            password_secret_name=mysql.password_secret_name,
            db_table=mysql.db_table,
            query=mysql.query,
        )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoJdbcSource:
        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                jdbcSource=ProtoJdbcSource(
                    url=self.url,
                    username_secret_name=self.username_secret_name,
                    password_secret_name=self.password_secret_name,
                    db_table=self.db_table,
                    query=self.query,
                    mysqlSource=ProtoMysqlSource(),
                ),
            ),
        )
