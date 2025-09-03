import uuid
from typing import Optional

from _qwak_proto.qwak.offline.serving.v1.offline_serving_async_service_pb2 import (
    GetFeatureValuesInRangeRequest,
    GetFeatureValuesInRangeResponse,
    GetFeatureValuesRequest,
    GetFeatureValuesResponse,
    GetFeatureValuesResultResponse,
    GetFileUploadUrlResponse,
)
from _qwak_proto.qwak.offline.serving.v1.offline_serving_async_service_pb2_grpc import (
    FeatureStoreOfflineServingAsyncServiceServicer,
)
from _qwak_proto.qwak.offline.serving.v1.options_pb2 import (
    OfflineServingQueryOptions as ProtoOfflineServingQueryOptions,
)


class FsOfflineServingServiceMock(FeatureStoreOfflineServingAsyncServiceServicer):
    def __init__(self):
        self.file_upload_url_response: Optional[GetFileUploadUrlResponse] = None
        self.response: Optional[GetFeatureValuesResultResponse] = None
        self.latest_query_options: Optional[ProtoOfflineServingQueryOptions] = None
        super(FsOfflineServingServiceMock, self).__init__()

    def given_next_file_upload_url(
        self, file_upload_url_response: GetFileUploadUrlResponse
    ):
        self.file_upload_url_response = file_upload_url_response

    def given_next_response(self, response: GetFeatureValuesResultResponse):
        self.response = response

    def GetFileUploadUrl(self, request, context) -> Optional[GetFileUploadUrlResponse]:
        return self.file_upload_url_response

    def GetFeatureValues(
        self, request: GetFeatureValuesRequest, context
    ) -> GetFeatureValuesResponse:
        request_id = str(uuid.uuid4())
        self.latest_query_options = request.options
        return GetFeatureValuesResponse(request_id=request_id)

    def GetFeatureValuesInRange(self, request: GetFeatureValuesInRangeRequest, context):
        request_id = str(uuid.uuid4())
        self.latest_query_options = request.options
        return GetFeatureValuesInRangeResponse(request_id=request_id)

    def GetFeatureValuesResult(
        self, request, context
    ) -> Optional[GetFeatureValuesResultResponse]:
        return self.response
