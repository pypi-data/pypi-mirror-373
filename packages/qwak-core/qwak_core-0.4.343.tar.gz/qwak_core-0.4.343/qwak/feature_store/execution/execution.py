import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

import boto3
import pandas as pd
from _qwak_proto.qwak.administration.authenticated_user.v1.authenticated_user_service_pb2 import (
    GetCloudCredentialsResponse,
)
from qwak.clients.administration import AuthenticatedUserClient
from qwak.exceptions import QwakException


class FeatureSetExecutionUnit:
    name: str
    feature_set_type: str
    owner: str
    description: str = ""
    display_name: str = ""
    fs_manager_client = None
    entity_name: str
    entity_key: str = None

    INGESTION_PREFIX: str = "batch_ingestion_data"
    BATCH_FEATURE_SET_TYPE: str = "batch_feature_set"

    def __init__(
        self,
        name,
        feature_set_type,
        owner,
        description,
        display_name,
        fs_manager_client,
        entity_name,
        entity_keys,
    ):
        self.name = name
        self.feature_set_type = feature_set_type
        self.owner = owner
        self.description = description
        self.display_name = display_name
        self.fs_manager_client = fs_manager_client
        self.entity_name = entity_name
        self.entity_key = entity_keys[0]  # Currently we support a single key

    def get_name(self):
        return self.name

    def get_feature_set_type(self):
        return self.feature_set_type

    def run_now_batch(self):
        """
        Used to trigger batch feature set now.

        Args:
            None
        Returns:
            None
        """
        self.fs_manager_client.run_feature_set(self.name)

    def validate_ingest_type(self):
        """
        validate the type of the feature set is Batch feature set type

        Return:
            None or raise exception if the type is incorrect
        """
        if self.feature_set_type != self.BATCH_FEATURE_SET_TYPE:
            raise QwakException(
                f"ingest is not supported for [{self.feature_set_type}]"
            )

    def _get_max_min_durations(self) -> Tuple[int, int]:
        """
        get max and min duration for ingestion

        Returns:
            max and min values
        """
        max_duration_seconds = 12 * 60 * 60
        min_duration_seconds = 15 * 60
        return max_duration_seconds, min_duration_seconds

    def _validate_duration_seconds(
        self,
        max_duration_seconds: int,
        min_duration_seconds: int,
        duration_seconds: int,
    ):
        """
        Validate duration second is in the range of the min/max durations
        Returtns:
        None or raise exception if not valid
        """
        if (
            duration_seconds > max_duration_seconds
            or duration_seconds < min_duration_seconds
        ):
            raise QwakException(
                "duration_seconds maximum is 12 hours and minimum of 15 minutes"
            )

    def ingest_pandas_df(
        self, df_to_ingest, timestamp_column: str, duration_seconds: int = 1800
    ):
        """
        Used to explicitly ingest a Pandas DF into a Qwak registered batch feature set

        Args:
            df_to_ingest: Pandas DataFrame, the pandas dataframe to ingest to the bach feature set
            timestamp_column: str, the name of the timestamp column
            duration_seconds: int, for how many seconds the STS credential's duration will be issued for.
             AWS limits this to max of 12 hours and min of 15 minutes.
        Returns:
            None
        """
        self.ingest(
            spark_context=None,
            df_to_ingest=df_to_ingest,
            timestamp_column=timestamp_column,
            duration_seconds=duration_seconds,
        )

    def ingest(
        self,
        spark_context,
        df_to_ingest,
        timestamp_column: str,
        duration_seconds: int = 3600,
        executors_temp_dir: Optional[str] = None,
    ):
        """
        Used to explicitly ingest a DF from a spark context or pandas into a Qwak registered batch feature set
        Args:
            spark_context: pyspark.context.SparkContext
            df_to_ingest: pyspark.sql.dataframe.DataFrame or pandas dataframe, the dataframe to ingest to the bach feature set
            timestamp_column: str, the name of the timestamp column
            duration_seconds: int, for how many seconds the STS credential's duration will be issued for.
             AWS limits this to max of 12 hours and min of 15 minutes.
             executors_temp_dir: Optional[str], if passed, on spark ingestion failure this function will try to
             ingest using the temp directory path. this path needs to be accessible on all spark executors.
             otherwise a random temp directory is used
        Returns:
            None
        """
        self.validate_ingest_type()

        max_duration_seconds, min_duration_seconds = self._get_max_min_durations()

        self._validate_duration_seconds(
            max_duration_seconds, min_duration_seconds, duration_seconds
        )

        is_spark_context = (
            False
            if spark_context is None and isinstance(df_to_ingest, pd.DataFrame)
            else True
        )

        validated_df = self._validate_and_format_df(
            df_to_ingest, timestamp_column, is_spark_context
        )

        authentication_client = AuthenticatedUserClient()
        auth_client_details = authentication_client.get_details()
        temporary_cloud_credentials = authentication_client.get_cloud_credentials(
            duration_seconds
        )

        write_path = self._ingest_dataframe(
            spark_context,
            validated_df,
            is_spark_context,
            temporary_cloud_credentials,
            auth_client_details,
            executors_temp_dir,
        )

        self._trigger_feature_set(timestamp_column, write_path)

    def _validate_and_format_df(self, df, timestamp_column, is_spark_context: bool):
        """
        Validate the data frame

        Args:
            df: pyspark.sql.dataframe.DataFrame, df to validate
            timestamp_column: str, the name of the timestamp column
            is_spark_context: rather using spark or pandas
        Returns:
            validated and formatted df
        """
        if self.entity_key not in df.columns:
            raise QwakException(
                f"entity key column [{self.entity_key}] was not found in the DFs columns"
            )
        return self._validate_and_cast_date_column_to_timestamp(
            df, timestamp_column, is_spark_context
        )

    @staticmethod
    def _get_date_column_from_pandas_df(df, timestamp_column):
        """
        get relevant column from pandas data frame
        Args:
            df: pandas data frame
            timestamp_column: the time column name
        """

        date_column = [
            column_name for column_name in df.columns if column_name == timestamp_column
        ]
        return date_column

    @staticmethod
    def _get_date_column_from_spark_df(df, timestamp_column):
        """
        get relevant columns from spark dataframe
        Args:
            df: pyspark.sql.dataframe.DataFrame
            timestamp_column: the time column name
        returns:
            date column
        """
        date_column = [
            (column_name, dtype)
            for column_name, dtype in df.dtypes
            if column_name == timestamp_column
        ]
        return date_column

    def _validate_and_cast_date_column_to_timestamp(
        self, df, timestamp_column: str, is_spark_context: bool
    ):
        """
        Validate and cast the data frames' timestamp column

        Args:
            df: pyspark.sql.dataframe.DataFrame, df to validate
            timestamp_column: str, the name of the timestamp column
            is_spark_context: rather using spark or not
        Returns:
            validated and casted timestamp column df
        """

        date_column = (
            self._get_date_column_from_spark_df(df, timestamp_column)
            if is_spark_context
            else self._get_date_column_from_pandas_df(df, timestamp_column)
        )

        if not date_column:
            raise QwakException(
                f"defined timestamp column: [{timestamp_column}] was not found in the DF"
            )
        if is_spark_context:
            if date_column[0][1] != "timestamp":
                try:
                    from pyspark.sql.functions import col
                    from pyspark.sql.types import TimestampType

                    df = df.withColumn(
                        timestamp_column, col(timestamp_column).cast(TimestampType())
                    )
                    return df

                except Exception as e:
                    raise QwakException(
                        f"failed to cast: [{timestamp_column}] to TimestampType, error is: [{e}]"
                    )
        elif isinstance(df, pd.DataFrame):
            return df
        else:
            raise QwakException(
                f"failed to cast: [{timestamp_column}]. Not supported type of dataframe"
            )
        return df

    def write_spark_df_to_s3(
        self, spark_context, bucket, aws_temporary_credentials, df_to_ingest, write_path
    ):
        """
        write spark dataframe to s3
        Args:
            spark_context: the spark session
            bucket: bucket name
            aws_temporary_credentials: temporary credentials for writing to s3
            df_to_ingest: Dataframe to ingest
            write_path: path to write in s3

        Returns:
            write_path - path to parquets files
        """

        with self._set_aws_auth_credentials(
            spark_context,
            bucket,
            aws_temporary_credentials,
        ):
            df_to_ingest.write.parquet(write_path)
            return f"{write_path}/*"

    def _create_s3_boto_client(self, aws_temporary_credentials):
        aws_permissions_dict = {
            "aws_access_key_id": aws_temporary_credentials.access_key_id,
            "aws_secret_access_key": aws_temporary_credentials.secret_access_key,
            "aws_session_token": aws_temporary_credentials.session_token,
        }
        return boto3.Session(**aws_permissions_dict).client("s3")

    def write_pandas_df_to_s3(
        self, aws_temporary_credentials, bucket, df_to_ingest, write_path
    ):
        """
        write pandas dataframe to s3
        Args:
            aws_temporary_credentials: temporary credentials for writing to s3
            bucket: bucket name
            df_to_ingest: Dataframe to ingest
            write_path: path to write in s3
        Returns:
            None
        """

        s3_client = self._create_s3_boto_client(aws_temporary_credentials)
        out_buffer = BytesIO()
        df_to_ingest.to_parquet(out_buffer, index=False)
        filepath = write_path.split(f"{bucket}/")[1]
        s3_client.put_object(Bucket=bucket, Key=filepath, Body=out_buffer.getvalue())

    def _ingest_dataframe(
        self,
        spark_context,
        df_to_ingest,
        is_spark_context: bool,
        temporary_cloud_credentials: GetCloudCredentialsResponse,
        auth_client_details,
        executors_temp_dir: Optional[str],
    ) -> str:
        """
        Dump a dataframe to a cloud path

        Args:
            spark_context: pyspark.context.SparkContext
            df_to_ingest: pyspark.sql.dataframe.DataFrame, the spark dataframe to ingest to the bach feature set
            creds_duration_seconds: int, for how many seconds the STS credential's duration will be issued for.
             AWS limits this to max of 12 hours and min of 15 minutes.
            is_spark_context: Rather using spark or pandas
            executors_temp_dir: Optional[str], if passed, on spark ingestion failure this function will try to
             ingest using the temp directory path. this path needs to be accessible on all spark executors.
             otherwise a random temp directory is used
              Returns:
                Parquet dump path
        """
        credentials_type = temporary_cloud_credentials.cloud_credentials.WhichOneof(
            "credentials"
        )
        if credentials_type == "aws_temporary_credentials":
            bucket = auth_client_details.environment.configuration.object_storage_bucket

            aws_temporary_credentials = (
                temporary_cloud_credentials.cloud_credentials.aws_temporary_credentials
            )

            write_path = self._get_s3_ingestion_path(bucket)
            try:
                if is_spark_context:
                    try:
                        write_path = self.write_spark_df_to_s3(
                            spark_context,
                            bucket,
                            aws_temporary_credentials,
                            df_to_ingest,
                            write_path,
                        )
                        return write_path
                    except Exception:
                        logging.info(
                            "Ingesting dataframe using a local buffer directory"
                        )
                        write_path = self._write_df_as_parquet(
                            executors_temp_dir,
                            df_to_ingest,
                            bucket,
                            aws_temporary_credentials,
                            write_path,
                        )
                        return write_path

                elif not is_spark_context:
                    self.write_pandas_df_to_s3(
                        aws_temporary_credentials, bucket, df_to_ingest, write_path
                    )
                    return write_path
            except Exception as e:
                raise QwakException(f"Failed to write dataframe to s3, error is: [{e}]")
        else:
            raise QwakException("Received an unknown cloud credentials type")

    def _trigger_feature_set(self, timestamp_column: str, parquet_path: str):
        """
        Used to trigger a batch feature set on an explicit parquet path

        Args:
            timestamp_column: str, name of the timestamp column
            parquet_path: str, path to the parquet files to trigger the batch feature set upon
        Returns:
            None
        """
        self.fs_manager_client.run_parquet_batch_feature_set(
            feature_set_name=self.name,
            parquet_location=parquet_path,
            timestamp_column=timestamp_column,
        )

    def _get_s3_ingestion_path(self, bucket) -> str:
        """
        Used to trigger a batch feature set on an explicit parquet path

        Args:
            bucket: str,
        Returns:
            ingestion path
        """
        return (
            f"s3a://{bucket}/{self.INGESTION_PREFIX}/{self.name}/"
            f'{datetime.utcnow().strftime("%Y%m%dT%H%M%S")}/{uuid.uuid4()}'
        )

    @contextmanager
    def _set_aws_auth_credentials(
        self, spark_context, bucket: str, aws_temporary_credentials
    ):
        original_credentials_provider = spark_context._jsc.hadoopConfiguration().get(
            f"fs.s3a.bucket.{bucket}.aws.credentials.provider"
        )
        original_access_key_id = spark_context._jsc.hadoopConfiguration().get(
            f"fs.s3a.bucket.{bucket}.access.key"
        )
        original_secret_key = spark_context._jsc.hadoopConfiguration().get(
            f"fs.s3a.bucket.{bucket}.secret.key"
        )
        original_session_token = spark_context._jsc.hadoopConfiguration().get(
            f"fs.s3a.bucket.{bucket}.session.token"
        )

        spark_context._jsc.hadoopConfiguration().set(
            f"fs.s3a.bucket.{bucket}.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider",
        )
        spark_context._jsc.hadoopConfiguration().set(
            f"fs.s3a.bucket.{bucket}.access.key",
            aws_temporary_credentials.access_key_id,
        )
        spark_context._jsc.hadoopConfiguration().set(
            f"fs.s3a.bucket.{bucket}.secret.key",
            aws_temporary_credentials.secret_access_key,
        )
        spark_context._jsc.hadoopConfiguration().set(
            f"fs.s3a.bucket.{bucket}.session.token",
            aws_temporary_credentials.session_token,
        )
        yield

        self._replace_or_unset_hadoop_conf(
            spark_context,
            f"fs.s3a.bucket.{bucket}.aws.credentials.provider",
            original_credentials_provider,
        )
        self._replace_or_unset_hadoop_conf(
            spark_context,
            f"fs.s3a.bucket.{bucket}.access.key",
            original_access_key_id,
        )
        self._replace_or_unset_hadoop_conf(
            spark_context, f"fs.s3a.bucket.{bucket}.secret.key", original_secret_key
        )
        self._replace_or_unset_hadoop_conf(
            spark_context,
            f"fs.s3a.bucket.{bucket}.session.token",
            original_session_token,
        )

    @staticmethod
    def _replace_or_unset_hadoop_conf(spark_context, key, value):
        if value:
            spark_context._jsc.hadoopConfiguration().set(key, value)
        else:
            spark_context._jsc.hadoopConfiguration().unset(key)

    def _write_df_as_parquet(
        self,
        executors_temp_dir: Optional[str],
        df,
        s3_bucket: str,
        aws_temporary_credentials,
        s3_write_path: str,
    ):
        """
        Write the df as parquet file using, foreachPartition.
        each partition is written locally to each executor as a parquet file, and then uploaded to s3
        Args:
            executors_temp_dir: Optional[str], temp directory to us as parquet buffer, needs to exists on each executor
            df: pyspark.sql.dataframe.DataFrame, df to ingest
        """

        def _write_to_parquet(row_iter, temp_dir_path):
            import os
            import uuid

            if not os.access(temp_dir_path, os.W_OK):
                raise QwakException(f"`{temp_dir_path}` is not writeable")
            random_suffix = uuid.uuid4()
            materialized_rows = list(row_iter)
            columns = list(materialized_rows[0].asDict().keys())
            pd.DataFrame(materialized_rows, columns=columns).to_parquet(
                f"{temp_dir_path}/{random_suffix}.snappy.parquet"
            )

        def _upload_all_file_in_dir_to_s3(
            s3_client, s3_bucket, s3_write_path, temp_dir_path
        ):
            import glob
            import os

            files = glob.glob(temp_dir_path + "/*")
            filepath = s3_write_path.split(f"{s3_bucket}/")[1]
            try:
                for file in files:
                    s3_file = f"{filepath}/{os.path.basename(file)}"
                    s3_client.upload_file(file, s3_bucket, s3_file)
            except Exception as e:
                raise QwakException(
                    f"An unexpected error occurred uploading the data files to S3, got [{e}]"
                )

        def ingest_partition_to_s3_using_local_dir_buffer(
            row_iter: List[dict],
            s3_bucket: str,
            aws_permissions_dict: dict,
            s3_write_path: str,
            executors_temp_dir: str,
        ):
            """
            This method runs in parallel on each spark executor.
            Currently the whole logic is implemented here in order to avoid serialization problems.
            Args:
                row_iter: Iter[Row], the partition to ingest
                aws_permissions_dict: dict[str -> str], aws credentials dict
                s3_write_path: str,  s3 path for where to upload parquet files
                executors_temp_dir: str,  local directory on each executor to use as a local buffer
            """
            _write_to_parquet(row_iter, executors_temp_dir)

            s3_client = boto3.Session(
                aws_access_key_id=aws_permissions_dict["key"],
                aws_secret_access_key=aws_permissions_dict["secret"],
                aws_session_token=aws_permissions_dict["token"],
            ).client("s3")

            _upload_all_file_in_dir_to_s3(
                s3_client, s3_bucket, s3_write_path, executors_temp_dir
            )

        if not executors_temp_dir:
            import tempfile

            temp_dir = tempfile.TemporaryDirectory()
            executors_temp_dir = temp_dir.name

        aws_permissions_dict = {
            "key": aws_temporary_credentials.access_key_id,
            "secret": aws_temporary_credentials.secret_access_key,
            "token": aws_temporary_credentials.session_token,
        }

        lambda_injected_with_variables = (
            lambda row_iter: ingest_partition_to_s3_using_local_dir_buffer(
                row_iter,
                s3_bucket,
                aws_permissions_dict,
                s3_write_path,
                executors_temp_dir,
            )
        )
        df.foreachPartition(lambda_injected_with_variables)
        return f"{s3_write_path}/*"
