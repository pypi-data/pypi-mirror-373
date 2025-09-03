from collections import defaultdict
from typing import Dict, List

from frogml._proto.qwak.file_versioning.file_versioning_pb2 import FileTagSpec
from frogml._proto.qwak.file_versioning.file_versioning_service_pb2 import (
    GetModelFileTagsRequest,
    GetModelFileTagsResponse,
    RegisterFileTagRequest,
    RegisterFileTagResponse,
)
from frogml._proto.qwak.file_versioning.file_versioning_service_pb2_grpc import (
    FileVersioningManagementServiceServicer,
)
from frogml_services_mock.mocks.utils.exception_handlers import (
    raise_internal_grpc_error,
)


class FileVersioningServiceMock(FileVersioningManagementServiceServicer):
    def __init__(self):
        super(FileVersioningServiceMock, self).__init__()
        self.tags: Dict[str : List[FileTagSpec]] = defaultdict(list)

    def RegisterFileTag(
        self, request: RegisterFileTagRequest, context
    ) -> RegisterFileTagResponse:
        try:
            self.tags[request.file_tag_spec.build_id].append(request.file_tag_spec)
            return RegisterFileTagResponse()
        except Exception as e:
            raise_internal_grpc_error(context, e)

    def GetModelFileTags(
        self, request: GetModelFileTagsRequest, context
    ) -> GetModelFileTagsResponse:
        try:
            file_tags_list = []

            if not request.build_id:
                for all_file_tags in self.tags.values():
                    for file_tag in all_file_tags:
                        file_tags_list.append(file_tag)
            else:
                for file_tag_by_build_id in self.tags[request.build_id]:
                    if file_tag_by_build_id.model_id == request.model_id:
                        file_tags_list.append(file_tag_by_build_id)

            if request.filter:
                file_tags_list_filtered = list(file_tags_list)
                filter_type: str = request.filter.WhichOneof("filter")

                if filter_type == "tag_contains":
                    for file_tag in file_tags_list:
                        if request.filter.tag_contains not in file_tag.tag:
                            file_tags_list_filtered.remove(file_tag)

                if filter_type == "tag_prefix":
                    for file_tag in file_tags_list:
                        if not file_tag.tag.startswith(request.filter.tag_prefix):
                            file_tags_list_filtered.remove(file_tag)

                file_tags_list = file_tags_list_filtered

            return GetModelFileTagsResponse(file_tags=file_tags_list)
        except Exception as e:
            raise_internal_grpc_error(context, e)
