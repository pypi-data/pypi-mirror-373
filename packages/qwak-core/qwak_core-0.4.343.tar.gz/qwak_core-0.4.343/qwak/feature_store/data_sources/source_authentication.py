from abc import ABC, abstractmethod
from dataclasses import dataclass

from _qwak_proto.qwak.feature_store.sources.batch_pb2 import (
    AwsAssumeRoleAuthentication as ProtoAwsAssumeRoleAuthentication,
    AwsCredentialsAuthentication as ProtoAwsCredentialsAuthentication,
)


class AwsAuthentication(ABC):
    @abstractmethod
    def _to_proto(self):
        pass


@dataclass
class AwsAssumeRoleAuthentication(AwsAuthentication):
    role_arn: str

    def _to_proto(self):
        return ProtoAwsAssumeRoleAuthentication(role_arn=self.role_arn)


@dataclass
class AwsCredentialsAuthentication(AwsAuthentication):
    access_key_secret_name: str
    secret_key_secret_name: str

    def _to_proto(self):
        return ProtoAwsCredentialsAuthentication(
            access_key_secret_name=self.access_key_secret_name,
            secret_key_secret_name=self.secret_key_secret_name,
        )
