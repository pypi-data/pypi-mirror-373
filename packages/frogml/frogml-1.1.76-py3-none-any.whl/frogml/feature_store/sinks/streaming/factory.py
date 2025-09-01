from typing import cast

from frogml._proto.qwak.feature_store.sinks.sink_pb2 import KafkaSink as ProtoKafkaSink
from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    StreamingAttachmentPoint as ProtoStreamingAttachmentPoint,
)
from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    StreamingSink as ProtoStreamingSink,
)
from frogml.feature_store.data_sources.streaming.kafka.authentication import (
    BaseAuthentication,
)
from frogml.core.feature_store.sinks.base import BaseSink
from frogml.feature_store.sinks.kafka import KafkaSink
from frogml.feature_store.sinks.kafka import MessageFormat as KafkaMessageFormat
from frogml.core.feature_store.sinks.streaming.attachment import (
    OfflineStreamingAttachmentPoint,
    OnlineStreamingAttachmentPoint,
    StreamingAttachmentPoint,
)


class StreamingSinkFactory:
    @staticmethod
    def get_streaming_sink(proto_streaming_sink: ProtoStreamingSink) -> BaseSink:
        sink_type = proto_streaming_sink.WhichOneof("sink_type")

        auth_conf: BaseAuthentication  # noqa: F842
        if sink_type == "kafka_sink":
            proto_kafka_sink: ProtoKafkaSink = proto_streaming_sink.kafka_sink
            auth_configuration: BaseAuthentication = cast(
                BaseAuthentication,
                BaseAuthentication._from_proto(proto_kafka_sink.auth_config),
            )
            return KafkaSink(
                name=proto_streaming_sink.name,
                topic=proto_kafka_sink.topic,
                bootstrap_servers=proto_kafka_sink.bootstrap_servers,
                message_format=KafkaMessageFormat(proto_kafka_sink.message_format),
                auth_configuration=auth_configuration,
                attachment_point=StreamingSinkFactory._get_attachment_point(
                    proto_streaming_sink.attachment_point
                ),
            )

    @staticmethod
    def _get_attachment_point(
        proto_attachment_point: ProtoStreamingAttachmentPoint,
    ) -> StreamingAttachmentPoint:
        attachment_point_type = proto_attachment_point.WhichOneof(
            "attachment_point_type"
        )
        if attachment_point_type == "online_streaming_attachment_point":
            return OnlineStreamingAttachmentPoint()
        elif attachment_point_type == "offline_streaming_attachment_point":
            return OfflineStreamingAttachmentPoint()
        else:
            raise ValueError(
                f"Unidentified streaming attachment point type: {attachment_point_type}"
            )
