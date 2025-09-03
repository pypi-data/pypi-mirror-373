from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    MongoSource as ProtoMongoSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource


@dataclass
class MongoDbSource(BaseBatchSource):
    hosts: str
    username_secret_name: str
    password_secret_name: str
    database: str
    collection: str
    connection_params: str
    protocol: str = "mongodb"
    repository: Optional[str] = None

    @classmethod
    def _from_proto(cls, proto):
        mongo = proto.mongoSource
        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            hosts=mongo.hosts,
            username_secret_name=mongo.username_secret_name,
            password_secret_name=mongo.password_secret_name,
            database=mongo.database,
            collection=mongo.collection,
            connection_params=mongo.connection_params,
            protocol=mongo.protocol,
        )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoBatchSource:
        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                mongoSource=ProtoMongoSource(
                    hosts=self.hosts,
                    username_secret_name=self.username_secret_name,
                    password_secret_name=self.password_secret_name,
                    database=self.database,
                    collection=self.collection,
                    connection_params=self.connection_params,
                    protocol=self.protocol,
                ),
            ),
        )
