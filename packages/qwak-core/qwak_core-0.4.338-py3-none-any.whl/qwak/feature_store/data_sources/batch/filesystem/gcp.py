from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    FileSystemConfiguration as ProtoFileSystemConfiguration,
    GcsServiceAccountImpersonation as ProtoGcsServiceAccountImpersonation,
    GcsUnauthenticated as ProtoGcsUnauthenticated,
)
from qwak.exceptions import QwakException
from qwak.feature_store.data_sources.batch.filesystem.base_config import (
    FileSystemConfiguration,
)


@dataclass
class GcpGcsServiceAccountImpersonation(FileSystemConfiguration):
    service_account_user: str

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.service_account_user or not self.service_account_user.strip():
            raise QwakException(
                "Service account user is mandatory for GCS service account impersonation, blanks are invalid"
            )

    def _to_proto(self):
        return ProtoFileSystemConfiguration(
            gcs_service_account_impersonation=ProtoGcsServiceAccountImpersonation(
                service_account_user=self.service_account_user
            )
        )

    @classmethod
    def _from_proto(cls, proto):
        return GcpGcsServiceAccountImpersonation(
            service_account_user=proto.service_account_user
        )


@dataclass
class GcpGcsUnauthenticated(FileSystemConfiguration):
    def _to_proto(self):
        return ProtoFileSystemConfiguration(
            gcs_unauthenticated=ProtoGcsUnauthenticated()
        )

    @classmethod
    def _from_proto(cls, proto):
        return GcpGcsUnauthenticated()
