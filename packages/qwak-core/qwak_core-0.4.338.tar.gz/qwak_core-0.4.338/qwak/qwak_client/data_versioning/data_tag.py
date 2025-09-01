from dataclasses import dataclass, field

from _qwak_proto.qwak.data_versioning.data_versioning_pb2 import (
    DataTagSpec as DataTagSpecProto,
)


@dataclass
class DataTag:
    model_id: str = field(default=None)
    build_id: str = field(default=None)
    tag: str = field(default=None)
    extension_type: str = field(default=None)
    environment_id: str = field(default=None)

    @staticmethod
    def from_proto(data_versioning_spec_proto: DataTagSpecProto):
        return DataTag(
            model_id=data_versioning_spec_proto.model_id,
            build_id=data_versioning_spec_proto.build_id,
            tag=data_versioning_spec_proto.tag,
            extension_type=data_versioning_spec_proto.extension_type,
            environment_id=data_versioning_spec_proto.environment_id,
        )
