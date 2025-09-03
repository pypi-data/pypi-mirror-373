from abc import ABC, abstractmethod
from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.sinks.sink_pb2 import (
    StreamingSink as ProtoStreamingSink,
)


@dataclass
class BaseSink(ABC):
    name: str

    @abstractmethod
    def to_proto_streaming_sink(self) -> ProtoStreamingSink:
        pass

    def __post_init__(self):
        pass
