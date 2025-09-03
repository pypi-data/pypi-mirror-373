from abc import ABC, abstractmethod
from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.sinks.sink_pb2 import (
    OfflineStreamingAttachmentPoint as ProtoOfflineStreamingAttachmentPoint,
    OnlineStreamingAttachmentPoint as ProtoOnlineStreamingAttachmentPoint,
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
