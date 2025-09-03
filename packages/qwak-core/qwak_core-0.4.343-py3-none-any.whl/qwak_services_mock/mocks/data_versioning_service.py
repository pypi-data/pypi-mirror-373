from collections import defaultdict
from typing import Dict, List

from _qwak_proto.qwak.data_versioning.data_versioning_pb2 import DataTagSpec
from _qwak_proto.qwak.data_versioning.data_versioning_service_pb2 import (
    GetModelDataTagsRequest,
    GetModelDataTagsResponse,
    RegisterDataTagRequest,
    RegisterDataTagResponse,
)
from _qwak_proto.qwak.data_versioning.data_versioning_service_pb2_grpc import (
    DataVersioningManagementServiceServicer,
)
from qwak_services_mock.mocks.utils.exception_handlers import raise_internal_grpc_error


class DataVersioningServiceMock(DataVersioningManagementServiceServicer):
    def __init__(self):
        super(DataVersioningServiceMock, self).__init__()
        self.tags: Dict[str : List[DataTagSpec]] = defaultdict(list)

    def RegisterDataTag(
        self, request: RegisterDataTagRequest, context
    ) -> RegisterDataTagResponse:
        try:
            self.tags[request.data_tag_spec.build_id].append(request.data_tag_spec)
            return RegisterDataTagResponse()
        except Exception as e:
            raise_internal_grpc_error(context, e)

    def GetModelDataTags(
        self, request: GetModelDataTagsRequest, context
    ) -> GetModelDataTagsResponse:
        try:
            data_tags_list = []

            if not request.build_id:
                for all_data_tags in self.tags.values():
                    for data_tag in all_data_tags:
                        data_tags_list.append(data_tag)
            else:
                for data_tag_by_build_id in self.tags[request.build_id]:
                    if data_tag_by_build_id.model_id == request.model_id:
                        data_tags_list.append(data_tag_by_build_id)

            if request.filter:
                filter_type: str = request.filter.WhichOneof("filter")

                if filter_type == "tag_contains":
                    for data_tag in data_tags_list:
                        if request.filter.tag_contains not in data_tag.tag:
                            data_tags_list.remove(data_tag)

                if filter_type == "tag_prefix":
                    for data_tag in data_tags_list:
                        if not data_tag.tag.startswith(request.filter.tag_prefix):
                            data_tags_list.remove(data_tag)

            return GetModelDataTagsResponse(data_tags=data_tags_list)
        except Exception as e:
            raise_internal_grpc_error(context, e)
