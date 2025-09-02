from dataclasses import dataclass, field
from enum import Enum

from frogml._proto.qwak.file_versioning.file_versioning_pb2 import (
    FileTagFilter as FileTagFilterProto,
)


class FileTagFilerType(Enum):
    FILE_TAG_FILTER_TYPE_INVALID = 0
    FILE_TAG_FILTER_TYPE_CONTAINS = 1
    FILE_TAG_FILTER_TYPE_PREFIX = 2


@dataclass
class FileTagFilter:
    value: str = field(default=None)
    type: FileTagFilerType = field(
        default=FileTagFilerType.FILE_TAG_FILTER_TYPE_INVALID
    )

    def to_proto(self):
        if self.type is FileTagFilerType.FILE_TAG_FILTER_TYPE_CONTAINS:
            return FileTagFilterProto(
                tag_contains=self.value,
            )
        elif self.type is FileTagFilerType.FILE_TAG_FILTER_TYPE_PREFIX:
            return FileTagFilterProto(
                tag_prefix=self.value,
            )
        else:
            return None
