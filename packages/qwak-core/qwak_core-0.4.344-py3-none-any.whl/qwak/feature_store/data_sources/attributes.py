from dataclasses import dataclass, field

from _qwak_proto.qwak.feature_store.sources.data_source_attribute_pb2 import (
    DataSourceAttributes as ProtoDataSourceAttributes,
    DataSourceAttributes,
)
from qwak.feature_store._common.source_code_spec import SourceCodeSpec


@dataclass
class DataSourceAttributes:
    source_code_spec: SourceCodeSpec = field(default_factory=lambda: SourceCodeSpec())

    def _to_proto(self) -> ProtoDataSourceAttributes:
        return ProtoDataSourceAttributes(
            source_code_spec=self.source_code_spec._to_proto()
        )

    @classmethod
    def _from_proto(cls, proto: ProtoDataSourceAttributes) -> DataSourceAttributes:
        return cls(
            source_code_spec=SourceCodeSpec._from_proto(proto=proto.source_code_spec)
        )
