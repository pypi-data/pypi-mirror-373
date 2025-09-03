from dataclasses import dataclass
from typing import Optional

from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    AnonymousS3Configuration as ProtoAnonymousS3Configuration,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    AwsS3AssumeRole as ProtoAwsS3AssumeRole,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    AwsS3FileSystemConfiguration as ProtoAwsS3FileSystemConfiguration,
)
from frogml._proto.qwak.feature_store.sources.batch_pb2 import (
    FileSystemConfiguration as ProtoFileSystemConfiguration,
)
from frogml.core.exceptions import FrogmlException
from frogml.feature_store.data_sources.batch.filesystem.base_config import (
    FileSystemConfiguration,
)


@dataclass
class AnonymousS3Configuration(FileSystemConfiguration):
    def _to_proto(self):
        return ProtoFileSystemConfiguration(
            aws_s3_anonymous=ProtoAnonymousS3Configuration()
        )

    @classmethod
    def _from_proto(cls, proto):
        return cls()


@dataclass
class AwsS3AssumeRoleFileSystemConfiguration(FileSystemConfiguration):
    role_arn: str

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.role_arn:
            raise FrogmlException("`role_arn` field is mandatory")

    def _to_proto(self) -> ProtoAwsS3FileSystemConfiguration:
        return ProtoFileSystemConfiguration(
            aws_s3_assume_role_configuration=ProtoAwsS3AssumeRole(
                role_arn=self.role_arn
            )
        )

    @classmethod
    def _from_proto(cls, proto: ProtoAwsS3AssumeRole):
        return cls(proto.role_arn)


@dataclass
class AwsS3FileSystemConfiguration(FileSystemConfiguration):
    access_key_secret_name: str
    secret_key_secret_name: str
    bucket: str
    session_token_secret_name: Optional[str] = ""

    def __post_init__(self):
        self._validate()

    def _validate(self):
        error_msg = "{field} field is mandatory"
        if not self.access_key_secret_name:
            raise FrogmlException(error_msg.format(field="access_key"))
        if not self.secret_key_secret_name:
            raise FrogmlException(error_msg.format(field="secret_key"))
        if not self.bucket:
            raise FrogmlException(error_msg.format(field="bucket"))

    def _to_proto(self):
        return ProtoFileSystemConfiguration(
            aws_s3_configuration=ProtoAwsS3FileSystemConfiguration(
                access_key_secret_name=self.access_key_secret_name,
                secret_key_secret_name=self.secret_key_secret_name,
                bucket=self.bucket,
                session_token_secret_name=self.session_token_secret_name,
            )
        )

    @classmethod
    def _from_proto(cls, proto):
        return AwsS3FileSystemConfiguration(
            access_key_secret_name=proto.access_key_secret_name,
            secret_key_secret_name=proto.secret_key_secret_name,
            bucket=proto.bucket,
            session_token_secret_name=proto.session_token_secret_name,
        )
