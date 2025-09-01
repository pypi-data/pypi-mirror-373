from typing import List

from frogml._proto.jfml.model_version.v1.artifact_pb2 import (
    Artifact as ArtifactProto,
    Checksums as ChecksumsProto,
)
from frogml.storage.models.entity_manifest import Artifact


class ProtoUtils:

    @staticmethod
    def convert_artifacts_to_artifacts_proto(
        artifacts: List[Artifact],
    ) -> List[ArtifactProto]:
        return [
            ArtifactProto(
                artifact_path=artifact.artifact_path,
                size=artifact.size,
                checksums=ChecksumsProto(sha2=artifact.checksums.sha2),
            )
            for artifact in artifacts
        ]
