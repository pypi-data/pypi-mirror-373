from dataclasses import dataclass
from typing import Optional

from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    AthenaSourceV1 as ProtoAthenaSourceV1,
    AwsAssumeRoleAuthentication as ProtoAwsAssumeRoleAuthentication,
    AwsAuthentication as ProtoAwsAuthentication,
    AwsCredentialsAuthentication as ProtoAwsCredentialsAuthentication,
    BatchSource as ProtoBatchSource,
    DatePartitionColumns as ProtoDatePartitionColumns,
    JdbcSource as ProtoJdbcSource,
    TimeFragmentedPartitionColumns as ProtoTimeFragmentedPartitionColumns,
)
from _qwak_proto.qwak.feature_store.sources.data_source_pb2 import (
    DataSourceSpec as ProtoDataSourceSpec,
)
from qwak.feature_store.data_sources.batch._jdbc import JdbcSource
from qwak.feature_store.data_sources.source_authentication import (
    AwsAssumeRoleAuthentication,
    AwsAuthentication,
    AwsCredentialsAuthentication,
)
from qwak.feature_store.data_sources.time_partition_columns import (
    ColumnRepresentation,
    DatePartitionColumns,
    DayFragmentColumn,
    MonthFragmentColumn,
    TimeFragmentedPartitionColumns,
    TimePartitionColumns,
    YearFragmentColumn,
)


@dataclass
class AthenaSource(JdbcSource):
    aws_region: str = str()
    s3_output_location: str = str()
    aws_authentication: Optional[AwsAuthentication] = None
    time_partition_columns: Optional[TimePartitionColumns] = None
    workgroup: Optional[str] = None
    repository: Optional[str] = None

    def _validate(self):
        super()._validate()

        if self.aws_authentication is None:
            raise AttributeError("`aws_authentication` must be set")

        if not self.aws_region:
            raise AttributeError("`aws_region` must be set")

        if not self.s3_output_location and not self.workgroup:
            raise AttributeError(
                "At least one of: `s3_output_location`, `workgroup` must be set"
            )

    def _to_proto(self, artifact_url: Optional[str] = None):
        proto_date_partition_columns = None
        proto_time_fragment_partition_columns = None

        if self.time_partition_columns:
            proto_partition = self.time_partition_columns._to_proto()
            if isinstance(proto_partition, ProtoDatePartitionColumns):
                proto_date_partition_columns = proto_partition
            elif isinstance(proto_partition, ProtoTimeFragmentedPartitionColumns):
                proto_time_fragment_partition_columns = proto_partition
            else:
                raise ValueError(
                    f"Got an unsupported time partition column: {proto_partition}"
                )

        proto_aws_assume_role_authentication = None
        proto_aws_static_credentials_authentication = None

        proto_aws_authentication = self.aws_authentication._to_proto()
        if isinstance(proto_aws_authentication, ProtoAwsAssumeRoleAuthentication):
            proto_aws_assume_role_authentication = proto_aws_authentication
        elif isinstance(proto_aws_authentication, ProtoAwsCredentialsAuthentication):
            proto_aws_static_credentials_authentication = proto_aws_authentication

        proto_auth: AwsAuthentication = ProtoAwsAuthentication(
            aws_assume_role_authentication=proto_aws_assume_role_authentication,
            aws_static_credentials_authentication=proto_aws_static_credentials_authentication,
        )

        return ProtoDataSourceSpec(
            data_source_repository_name=self.repository,
            batch_source=ProtoBatchSource(
                name=self.name,
                description=self.description,
                date_created_column=self.date_created_column,
                jdbcSource=ProtoJdbcSource(
                    url=self.url,
                    username_secret_name=self.username_secret_name,
                    password_secret_name=self.password_secret_name,
                    db_table=self.db_table,
                    query=self.query,
                    athenaSource=ProtoAthenaSourceV1(
                        aws_authentication=proto_auth,
                        date_partition_columns=proto_date_partition_columns,
                        time_fragmented_partition_columns=proto_time_fragment_partition_columns,
                        s3_output_location=self.s3_output_location,
                        aws_region=self.aws_region,
                        workgroup=self.workgroup,
                    ),
                ),
            ),
        )

    @classmethod
    def _from_proto(cls, proto: ProtoBatchSource):
        proto_jdbc_source: ProtoJdbcSource = proto.jdbcSource
        proto_athena_source: ProtoAthenaSourceV1 = proto_jdbc_source.athenaSource

        aws_authentication: AwsAuthentication = (
            AthenaSource._extract_and_configure_aws_authentication(
                proto_athena_source.aws_authentication
            )
        )

        time_partition_columns: Optional[TimePartitionColumns] = (
            AthenaSource._extract_partition_column(proto_athena_source)
        )
        workgroup: Optional[str] = (
            proto_athena_source.workgroup
            if proto_athena_source.HasField("workgroup")
            else None
        )

        return cls(
            name=proto.name,
            date_created_column=proto.date_created_column,
            description=proto.description,
            password_secret_name=proto_jdbc_source.password_secret_name,
            username_secret_name=proto_jdbc_source.username_secret_name,
            db_table=proto_jdbc_source.db_table,
            query=proto_jdbc_source.query,
            aws_authentication=aws_authentication,
            time_partition_columns=time_partition_columns,
            aws_region=proto_athena_source.aws_region,
            s3_output_location=proto_athena_source.s3_output_location,
            workgroup=workgroup,
        )

    @staticmethod
    def _extract_and_configure_aws_authentication(
        proto_aws_authentication: ProtoAwsAuthentication,
    ) -> AwsAuthentication:
        auth_type = proto_aws_authentication.WhichOneof("type")

        if auth_type == "aws_static_credentials_authentication":
            proto_aws_authentication = (
                AthenaSource._extract_and_configure_aws_credentials_auth(
                    proto_aws_authentication.aws_static_credentials_authentication
                )
            )
        elif auth_type == "aws_assume_role_authentication":
            proto_aws_authentication = AthenaSource._extract_aws_assume_role_auth(
                proto_aws_authentication.aws_assume_role_authentication
            )
        else:
            raise ValueError(
                f"Got an unsupported aws authentication method: {proto_aws_authentication}"
            )

        return proto_aws_authentication

    @staticmethod
    def _extract_and_configure_aws_credentials_auth(
        proto_aws_creds: ProtoAwsCredentialsAuthentication,
    ) -> AwsCredentialsAuthentication:
        return AwsCredentialsAuthentication(
            access_key_secret_name=proto_aws_creds.access_key_secret_name,
            secret_key_secret_name=proto_aws_creds.secret_key_secret_name,
        )

    @staticmethod
    def _extract_aws_assume_role_auth(
        proto_aws_assume_role: ProtoAwsAssumeRoleAuthentication,
    ) -> AwsAssumeRoleAuthentication:
        return AwsAssumeRoleAuthentication(
            role_arn=proto_aws_assume_role.role_arn,
        )

    @staticmethod
    def _extract_partition_column(
        proto_athena_source: ProtoAthenaSourceV1,
    ) -> Optional[TimePartitionColumns]:
        if proto_athena_source.HasField("time_partition_columns"):
            partition_cols_type = proto_athena_source.WhichOneof(
                "time_partition_columns"
            )

            if partition_cols_type == "date_partition_columns":
                res = DatePartitionColumns(
                    date_column_name=proto_athena_source.date_partition_columns.date_column_name,
                    date_format=proto_athena_source.date_partition_columns.date_format,
                )
            elif partition_cols_type == "time_fragmented_partition_columns":
                year_rep = AthenaSource._extract_column_representation(
                    proto_athena_source.time_fragmented_partition_columns.year_partition_column
                )

                year_fragment_col = YearFragmentColumn(
                    column_name=proto_athena_source.time_fragmented_partition_columns.year_partition_column.column_name,
                    representation=year_rep,
                )

                month_fragment_col = None
                if proto_athena_source.time_fragmented_partition_columns.HasField(
                    "month_partition_column"
                ):
                    month_rep = AthenaSource._extract_column_representation(
                        proto_athena_source.time_fragmented_partition_columns.month_partition_column
                    )

                    month_fragment_col = MonthFragmentColumn(
                        column_name=proto_athena_source.time_fragmented_partition_columns.month_partition_column.column_name,
                        representation=month_rep,
                    )

                day_fragment_col = None
                if proto_athena_source.time_fragmented_partition_columns.HasField(
                    "day_partition_column"
                ):
                    day_rep = AthenaSource._extract_column_representation(
                        proto_athena_source.time_fragmented_partition_columns.day_partition_column
                    )

                    day_fragment_col = DayFragmentColumn(
                        column_name=proto_athena_source.time_fragmented_partition_columns.day_partition_column.column_name,
                        representation=day_rep,
                    )

                res = TimeFragmentedPartitionColumns(
                    year_partition_column=year_fragment_col,
                    month_partition_column=month_fragment_col,
                    day_partition_column=day_fragment_col,
                )
            else:
                raise ValueError(
                    f"Got an unsupported time partition column: {proto_athena_source}"
                )
        else:
            res = None

        return res

    @staticmethod
    def _extract_column_representation(proto_fragment_column):
        column_rep = proto_fragment_column.WhichOneof("column_representation")

        if column_rep == "numeric_column_representation":
            res = ColumnRepresentation.NumericColumnRepresentation
        elif column_rep == "textual_column_representation":
            res = ColumnRepresentation.TextualColumnRepresentation
        else:
            raise ValueError(f"Unsupported ColumnRepresentation: {column_rep}")

        return res
