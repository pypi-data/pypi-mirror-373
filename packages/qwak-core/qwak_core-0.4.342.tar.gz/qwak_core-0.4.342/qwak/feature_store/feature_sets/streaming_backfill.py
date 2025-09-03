from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Set, Union

from _qwak_proto.qwak.feature_store.features.execution_pb2 import (
    BackfillExecutionSpec as ProtoBackfillExecutionSpec,
)
from _qwak_proto.qwak.feature_store.features.feature_set_types_pb2 import (
    BackfillBatchDataSourceSpec as ProtoBackfillBatchDataSourceSpec,
    BackfillDataSourceSpec as ProtoBackfillDataSourceSpec,
    BackfillSpec as ProtoBackfillSpec,
)
from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    BatchSource as ProtoBatchSource,
)
from google.protobuf.timestamp_pb2 import Timestamp as ProtoTimestamp
from qwak.clients.feature_store import FeatureRegistryClient
from qwak.exceptions import QwakException
from qwak.feature_store._common.artifact_utils import ArtifactSpec, ArtifactsUploader
from qwak.feature_store._common.feature_set_utils import get_batch_source_for_featureset
from qwak.feature_store.feature_sets.execution_spec import ClusterTemplate
from qwak.feature_store.feature_sets.transformations import SparkSqlTransformation

_BACKFILL_ = "_qwak_backfill_specification"


@dataclass
class DataSourceBackfillSpec(ABC):
    data_source_name: str

    @abstractmethod
    def _to_proto(self, feature_registry: FeatureRegistryClient):
        pass

    @classmethod
    def _from_proto(cls, proto: ProtoBackfillDataSourceSpec):
        function_mapping = {"batch_data_source_spec": BackfillBatchDataSourceSpec}

        backfill_source_type: str = proto.WhichOneof("type")

        if backfill_source_type in function_mapping:
            function_class = function_mapping.get(backfill_source_type)
            return function_class._from_proto(proto)

        raise QwakException(
            f"Got unsupported backfill source type {backfill_source_type} for streaming backfill"
        )


@dataclass
class BackfillBatchDataSourceSpec(DataSourceBackfillSpec):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None

    def _to_proto(
        self, feature_registry: FeatureRegistryClient
    ) -> ProtoBackfillBatchDataSourceSpec:
        start_timestamp: Optional[ProtoTimestamp] = None
        end_timestamp: Optional[ProtoTimestamp] = None

        if self.end_datetime:
            end_timestamp = ProtoTimestamp()
            end_timestamp.FromDatetime(self.end_datetime.astimezone(timezone.utc))

        if self.start_datetime:
            start_timestamp = ProtoTimestamp()
            start_timestamp.FromDatetime(self.start_datetime.astimezone(timezone.utc))

        proto_data_source: ProtoBatchSource = get_batch_source_for_featureset(
            batch_ds_name=self.data_source_name, feature_registry=feature_registry
        )

        return ProtoBackfillBatchDataSourceSpec(
            data_source=proto_data_source,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

    @classmethod
    def _from_proto(
        cls, proto: ProtoBackfillDataSourceSpec
    ) -> "BackfillBatchDataSourceSpec":
        start_datetime: Optional[datetime] = None
        end_datetime: Optional[datetime] = None

        batch_backfill_spec: ProtoBackfillBatchDataSourceSpec = (
            proto.batch_data_source_spec
        )

        proto_start_timestamp: ProtoTimestamp = batch_backfill_spec.start_timestamp
        proto_end_timestamp: ProtoTimestamp = batch_backfill_spec.end_timestamp

        start_datetime = datetime.fromtimestamp(
            proto_start_timestamp.seconds + proto_start_timestamp.nanos / 1e9
        )

        end_datetime = datetime.fromtimestamp(
            proto_end_timestamp.seconds + proto_end_timestamp.nanos / 1e9
        )

        return cls(
            data_source_name=batch_backfill_spec.data_source.name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )


@dataclass
class StreamingBackfill:
    start_datetime: datetime
    end_datetime: datetime
    data_sources_specs: List[DataSourceBackfillSpec]
    transform: "SparkSqlTransformation"
    cluster_template: Optional[ClusterTemplate] = ClusterTemplate.SMALL

    def __post_init__(self):
        if not self.data_sources_specs:
            raise QwakException(
                "Trying to create a streaming backfill with no data sources. "
                "At least one data source has to be provided when trying to create a streaming backfill."
            )

        if not self.start_datetime or not self.end_datetime:
            raise QwakException(
                "For backfill, start_datetime and end_datetime are mandatory fields."
            )

        if type(self.transform) is not SparkSqlTransformation:
            raise QwakException(
                "For backfill, only Spark SQL transformation type is currently supported"
            )

        self._validate_unique_sources()

    def _validate_unique_sources(self):
        source_names: List[str] = [
            data_source.data_source_name for data_source in self.data_sources_specs
        ]
        duplicates: Set[str] = {
            item for item in source_names if source_names.count(item) > 1
        }
        if duplicates:
            raise QwakException(
                f"A specific data source can only appear once per backfill definition. "
                f"Found these duplicates: {', '.join(set(duplicates))}"
            )

    def _validate_tile_size(self, initial_tile_size: int):
        if self.end_datetime.timestamp() % initial_tile_size != 0:
            raise QwakException(
                f"Chosen backfill end datetime is invalid,"
                f" it has to be exactly dividable by slice size of {initial_tile_size} seconds."
            )

    def _to_proto(
        self,
        feature_registry: FeatureRegistryClient,
        featureset_name: str,
        original_instance_module_path: str,
    ) -> ProtoBackfillSpec:
        artifact_url: Optional[str] = None
        artifact_spec: Optional[ArtifactSpec] = ArtifactsUploader.get_artifact_spec(
            transformation=self.transform,
            featureset_name=f"{featureset_name}-backfill",
            __instance_module_path__=original_instance_module_path,
        )

        if artifact_spec:
            artifact_url = ArtifactsUploader.upload(artifact_spec)

        end_timestamp = ProtoTimestamp()
        end_timestamp.FromDatetime(self.end_datetime.astimezone(timezone.utc))

        start_timestamp = ProtoTimestamp()
        start_timestamp.FromDatetime(self.start_datetime.astimezone(timezone.utc))

        return ProtoBackfillSpec(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            execution_spec=ProtoBackfillExecutionSpec(
                **{"cluster_template": ClusterTemplate.to_proto(self.cluster_template)}
            ),
            transformation=self.transform._to_proto(artifact_path=artifact_url),
            data_source_specs=[
                ProtoBackfillDataSourceSpec(
                    batch_data_source_spec=data_source_spec._to_proto(
                        feature_registry=feature_registry
                    )
                )
                for data_source_spec in self.data_sources_specs
            ],
        )

    @classmethod
    def _from_proto(cls, proto: ProtoBackfillSpec):
        datetime.fromtimestamp(
            proto.start_timestamp.seconds + proto.start_timestamp.nanos / 1e9
        )

        data_sources_specs = [
            BackfillBatchDataSourceSpec._from_proto(ds)
            for ds in proto.data_source_specs
        ]

        return cls(
            start_datetime=datetime.fromtimestamp(
                proto.start_timestamp.seconds + proto.start_timestamp.nanos / 1e9
            ),
            end_datetime=datetime.fromtimestamp(
                proto.end_timestamp.seconds + proto.end_timestamp.nanos / 1e9
            ),
            data_sources_specs=data_sources_specs,
            transform=SparkSqlTransformation._from_proto(
                proto.transformation.sql_transformation
            ),
        )

    @staticmethod
    def _get_normalized_backfill_sources_spec(
        data_sources: Union[List[str], List[DataSourceBackfillSpec]],
    ) -> List[DataSourceBackfillSpec]:
        # reformat all data source specs to 'DataSourceBackfillSpec'
        return [
            (
                BackfillBatchDataSourceSpec(data_source_name=data_source)
                if isinstance(data_source, str)
                else data_source
            )
            for data_source in data_sources
        ]

    @classmethod
    def set_streaming_backfill_on_function(
        cls,
        function,
        start_date: datetime,
        end_date: datetime,
        data_sources: Union[List[str], List[DataSourceBackfillSpec]],
        backfill_transformation: SparkSqlTransformation,
        backfill_cluster_template: Optional[ClusterTemplate] = ClusterTemplate.SMALL,
    ):
        setattr(
            function,
            _BACKFILL_,
            cls(
                start_datetime=start_date,
                end_datetime=end_date,
                data_sources_specs=StreamingBackfill._get_normalized_backfill_sources_spec(
                    data_sources
                ),
                transform=backfill_transformation,
                cluster_template=backfill_cluster_template,
            ),
        )

    @staticmethod
    def get_streaming_backfill_from_function(function):
        return getattr(function, _BACKFILL_, None)
