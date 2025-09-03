from dataclasses import dataclass
from enum import Enum
from typing import Optional

from frogml._proto.qwak.feature_store.sinks.sink_pb2 import KafkaSink as ProtoKafkaSink
from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    StreamingSink as ProtoStreamingSink,
)
from frogml._proto.qwak.feature_store.sources.streaming_pb2 import (
    MessageFormat as ProtoMessageFormat,
)
from frogml.core.exceptions import FrogmlException
from frogml.feature_store.data_sources.streaming.kafka.authentication import (
    BaseAuthentication,
)
from frogml.core.feature_store.sinks.base import BaseSink
from frogml.core.feature_store.sinks.streaming.attachment import (
    StreamingAttachmentPoint,
)


class MessageFormat(Enum):
    JSON = ProtoMessageFormat.JSON


@dataclass
class KafkaSink(BaseSink):
    topic: str
    bootstrap_servers: str
    message_format: MessageFormat
    auth_configuration: BaseAuthentication
    attachment_point: Optional[StreamingAttachmentPoint]

    def _to_proto_kafka_sink(self) -> ProtoKafkaSink:
        return ProtoKafkaSink(
            topic=self.topic,
            bootstrap_servers=self.bootstrap_servers,
            message_format=self.message_format.value,
            auth_config=self.auth_configuration._to_proto(),
        )

    def to_proto_streaming_sink(self) -> ProtoStreamingSink:
        if self.attachment_point is None:
            raise FrogmlException(
                "A Sink must have an attachment point configured in order for it to be used as a streaming sink"
            )

        proto_kafka_sink: ProtoKafkaSink = self._to_proto_kafka_sink()

        return ProtoStreamingSink(
            name=self.name,
            kafka_sink=proto_kafka_sink,
            attachment_point=self.attachment_point._to_proto(),
        )

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        pass
