import inspect
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional, Type

from frogml._proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    KafkaSourceV1 as ProtoKafkaSourceV1,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    StreamingSource as ProtoStreamingSource,
)
from frogml.core.exceptions import FrogmlException
from frogml.feature_store._common.artifact_utils import ArtifactSpec
from frogml.feature_store.data_sources.streaming._streaming import (
    BaseStreamingSource,
)
from frogml.feature_store.data_sources.streaming.kafka.authentication import (
    BaseAuthentication,
    SslAuthentication,
)
from frogml.feature_store.data_sources.streaming.kafka.deserialization import (
    Deserializer,
)


@dataclass
class KafkaSource(BaseStreamingSource):
    bootstrap_servers: str

    # Deserialization
    deserialization: Deserializer

    # secret configs, the value is resolved to the secret,
    # s.t. (key, value) -> (key, get_secret(value))
    # not all configs will be respected, this is a best-effort
    secret_configs: Dict[str, str] = field(default_factory=lambda: {})

    # passthrough configs - not all configs will be respected,
    # this is a best-effort
    passthrough_configs: Dict[str, str] = field(default_factory=lambda: {})

    # the following 3 are pairwise mutually exclusive
    assign: Optional[str] = None
    subscribe: Optional[str] = None
    subscribe_pattern: Optional[str] = None

    authentication_method: Optional[BaseAuthentication] = field(
        default_factory=lambda: SslAuthentication()
    )

    repository: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        num_defined = len(
            [
                _
                for _ in [self.assign, self.subscribe, self.subscribe_pattern]
                if _ is not None
            ]
        )
        if num_defined != 1:
            raise FrogmlException(
                "Exactly one of (assign, subscribe, subscribe_pattern) must be defined!"
            )

    def _get_artifacts(self) -> Optional["ArtifactSpec"]:
        deserializer_function: Optional[Callable] = self.deserialization._get_function()

        if deserializer_function:
            return ArtifactSpec(
                artifact_name=self.name,
                root_module_path=Path(
                    os.path.abspath(inspect.getfile(deserializer_function))
                ).parent,
                artifact_object=self.deserialization,
                callables=[deserializer_function],
                suffix="resource.zip",
            )

    def _to_proto(self, artifact_url: Optional[str] = None) -> ProtoDataSourceSpec:
        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            stream_source=ProtoStreamingSource(
                name=self.name,
                description=self.description,
                kafkaSourceV1=ProtoKafkaSourceV1(
                    bootstrap_servers=self.bootstrap_servers,
                    assign=self.assign,
                    subscribe=self.subscribe,
                    subscribe_pattern=self.subscribe_pattern,
                    secret_configs=self.secret_configs,
                    passthrough_configs=self.passthrough_configs,
                    authentication_method=self.authentication_method._to_proto(),
                    deserialization=self.deserialization._to_proto(
                        artifact_path=artifact_url
                    ),
                ),
            ),
        )

    @classmethod
    def _from_proto(cls, proto) -> Type["KafkaSource"]:
        kafka = proto.kafkaSourceV1
        topic_configuration_key = kafka.WhichOneof("topic_configuration")
        oneof_args = {topic_configuration_key: getattr(kafka, topic_configuration_key)}
        return cls(
            name=proto.name,
            description=proto.description,
            bootstrap_servers=kafka.bootstrap_servers,
            secret_configs=kafka.secret_configs,
            passthrough_configs=kafka.passthrough_configs,
            deserialization=Deserializer._from_proto(
                proto_deserializer=kafka.deserialization
            ),
            authentication_method=BaseAuthentication._from_proto(
                proto_authentication_method=kafka.authentication_method
            ),
            **oneof_args,
        )
