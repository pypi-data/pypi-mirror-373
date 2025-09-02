from abc import ABC, abstractmethod
from dataclasses import dataclass

from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    OfflineStreamingAttachmentPoint as ProtoOfflineStreamingAttachmentPoint,
)
from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    OnlineStreamingAttachmentPoint as ProtoOnlineStreamingAttachmentPoint,
)
from frogml._proto.qwak.feature_store.sinks.sink_pb2 import (
    StreamingAttachmentPoint as ProtoStreamingAttachmentPoint,
)


class StreamingAttachmentPoint(ABC):
    @abstractmethod
    def _to_proto(self) -> ProtoStreamingAttachmentPoint:
        pass


@dataclass
class OfflineStreamingAttachmentPoint(StreamingAttachmentPoint):
    def _to_proto(self) -> ProtoStreamingAttachmentPoint:
        return ProtoStreamingAttachmentPoint(
            offline_streaming_attachment_point=ProtoOfflineStreamingAttachmentPoint()
        )


@dataclass
class OnlineStreamingAttachmentPoint(StreamingAttachmentPoint):
    def _to_proto(self) -> ProtoStreamingAttachmentPoint:
        return ProtoStreamingAttachmentPoint(
            online_streaming_attachment_point=ProtoOnlineStreamingAttachmentPoint()
        )
