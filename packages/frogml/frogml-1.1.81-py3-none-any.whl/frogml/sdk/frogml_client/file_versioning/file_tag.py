from dataclasses import dataclass, field

from frogml._proto.qwak.file_versioning.file_versioning_pb2 import (
    FileTagSpec as FileTagSpecProto,
)


@dataclass
class FileTag:
    model_id: str = field(default=None)
    build_id: str = field(default=None)
    tag: str = field(default=None)
    extension_type: str = field(default=None)
    environment_id: str = field(default=None)

    @staticmethod
    def from_proto(file_versioning_spec_proto: FileTagSpecProto):
        return FileTag(
            model_id=file_versioning_spec_proto.model_id,
            build_id=file_versioning_spec_proto.build_id,
            tag=file_versioning_spec_proto.tag,
            extension_type=file_versioning_spec_proto.extension_type,
            environment_id=file_versioning_spec_proto.environment_id,
        )
