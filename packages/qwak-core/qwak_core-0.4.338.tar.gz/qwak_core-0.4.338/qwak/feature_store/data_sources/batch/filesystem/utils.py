from typing import Optional

from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    AnonymousS3Configuration as ProtoAnonymousS3Configuration,
    AwsS3AssumeRole as ProtoAwsS3AssumeRole,
    AwsS3FileSystemConfiguration as ProtoAwsS3FileSystemConfiguration,
    GcsServiceAccountImpersonation as ProtoGcsServiceAccountImpersonation,
    GcsUnauthenticated as ProtoGcsUnauthenticated,
)
from qwak.exceptions import QwakException
from qwak.feature_store.data_sources.batch.filesystem.aws import (
    AnonymousS3Configuration,
    AwsS3AssumeRoleFileSystemConfiguration,
    AwsS3FileSystemConfiguration,
)
from qwak.feature_store.data_sources.batch.filesystem.base_config import (
    FileSystemConfiguration,
)
from qwak.feature_store.data_sources.batch.filesystem.gcp import (
    GcpGcsServiceAccountImpersonation,
    GcpGcsUnauthenticated,
)


def get_fs_config_from_proto(filesystem_conf) -> Optional[FileSystemConfiguration]:
    if not filesystem_conf:
        return None

    fs_conf_type = filesystem_conf.WhichOneof("type")

    if not fs_conf_type:
        return None

    fs_conf = getattr(filesystem_conf, fs_conf_type)
    if isinstance(fs_conf, ProtoAwsS3FileSystemConfiguration):
        return AwsS3FileSystemConfiguration._from_proto(fs_conf)

    elif isinstance(fs_conf, ProtoAnonymousS3Configuration):
        return AnonymousS3Configuration._from_proto(fs_conf)

    elif isinstance(fs_conf, ProtoAwsS3AssumeRole):
        return AwsS3AssumeRoleFileSystemConfiguration._from_proto(fs_conf)

    elif isinstance(fs_conf, ProtoGcsServiceAccountImpersonation):
        return GcpGcsServiceAccountImpersonation._from_proto(fs_conf)

    elif isinstance(fs_conf, ProtoGcsUnauthenticated):
        return GcpGcsUnauthenticated._from_proto(fs_conf)

    else:
        raise QwakException(f"Unsupported FileSystemConfiguration: {fs_conf_type}")
