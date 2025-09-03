from dataclasses import dataclass, field
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    ParquetSource as ProtoParquetSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.feature_store.data_sources import AnonymousS3Configuration
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource
from frogml.feature_store.data_sources.batch.filesystem.base_config import (
    FileSystemConfiguration,
)
from frogml.feature_store.data_sources.batch.filesystem.utils import (
    get_fs_config_from_proto,
)


@dataclass
class ParquetSource(BaseBatchSource):
    path: str
    filesystem_configuration: FileSystemConfiguration = field(
        default_factory=lambda: AnonymousS3Configuration()
    )
    repository: Optional[str] = None

    @classmethod
    def _from_proto(cls, proto):
        parquet: ProtoParquetSource = proto.parquetSource
        fs_conf = get_fs_config_from_proto(parquet.filesystem_configuration)

        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            path=parquet.path,
            filesystem_configuration=fs_conf,
        )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoDataSourceSpec:
        fs_conf = None
        if self.filesystem_configuration:
            fs_conf = self.filesystem_configuration._to_proto()

        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                parquetSource=ProtoParquetSource(
                    path=self.path, filesystem_configuration=fs_conf
                ),
            ),
        )
