from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    CsvSource as ProtoCsvSource,
)
from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource
from frogml.feature_store.data_sources.batch.filesystem.base_config import (
    FileSystemConfiguration,
)
from frogml.feature_store.data_sources.batch.filesystem.utils import (
    get_fs_config_from_proto,
)


@dataclass
class CsvSource(BaseBatchSource):
    path: str
    quote_character: str = '"'
    escape_character: str = '"'
    filesystem_configuration: Optional[FileSystemConfiguration] = None
    repository: Optional[str] = None

    @classmethod
    def _from_proto(cls, proto):
        csv = proto.csvSource

        fs_conf = get_fs_config_from_proto(csv.filesystem_configuration)

        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            path=csv.path,
            quote_character=csv.quote_character,
            escape_character=csv.escape_character,
            filesystem_configuration=fs_conf,
        )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoDataSourceSpec:
        fs_conf = None
        if self.filesystem_configuration:
            fs_conf = self.filesystem_configuration._to_proto()

        return ProtoDataSourceSpec(
            featureset_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                csvSource=ProtoCsvSource(
                    path=self.path,
                    quote_character=self.quote_character,
                    escape_character=self.escape_character,
                    filesystem_configuration=fs_conf,
                ),
            ),
        )
