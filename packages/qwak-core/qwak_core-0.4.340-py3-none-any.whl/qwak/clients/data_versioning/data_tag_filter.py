from dataclasses import dataclass, field
from enum import Enum

from _qwak_proto.qwak.data_versioning.data_versioning_pb2 import (
    DataTagFilter as DataTagFilterProto,
)


class DataTagFilerType(Enum):
    DATA_TAG_FILTER_TYPE_INVALID = 0
    DATA_TAG_FILTER_TYPE_CONTAINS = 1
    DATA_TAG_FILTER_TYPE_PREFIX = 2


@dataclass
class DataTagFilter:
    value: str = field(default=None)
    type: DataTagFilerType = field(
        default=DataTagFilerType.DATA_TAG_FILTER_TYPE_INVALID
    )

    def to_proto(self):
        if self.type is DataTagFilerType.DATA_TAG_FILTER_TYPE_CONTAINS:
            return DataTagFilterProto(
                tag_contains=self.value,
            )
        elif self.type is DataTagFilerType.DATA_TAG_FILTER_TYPE_PREFIX:
            return DataTagFilterProto(
                tag_prefix=self.value,
            )
        else:
            return None
