from typing import Dict, Optional

import grpc
from _qwak_proto.qwak.service_discovery.service_discovery_location_pb2 import (
    ServiceLocationDescriptor,
)
from _qwak_proto.qwak.service_discovery.service_discovery_location_service_pb2 import (
    GetServingUrlRequestResponse,
)
from _qwak_proto.qwak.service_discovery.service_discovery_location_service_pb2_grpc import (
    LocationDiscoveryServiceServicer,
)


class LocationDiscoveryServiceApiMock(LocationDiscoveryServiceServicer):
    """
    Mock implementation of the LocationDiscoveryService for testing SDK behavior.
    Allows setting mock responses and optional error codes for each endpoint.
    """

    def __init__(self):
        super().__init__()
        self._responses: Dict[str, Optional[ServiceLocationDescriptor]] = {}
        self._error_codes: Dict[str, grpc.StatusCode] = {}

    def _set_mock(
        self,
        key: str,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._responses[key] = response
        self._error_codes[key] = error_code

    def _handle(
        self, key: str, context: grpc.ServicerContext
    ) -> GetServingUrlRequestResponse:
        response = self._responses.get(key)
        if response:
            return GetServingUrlRequestResponse(location=response)
        context.set_code(self._error_codes.get(key, grpc.StatusCode.NOT_FOUND))
        context.set_details(f"No mock response set for {key}")
        return GetServingUrlRequestResponse()

    # Setters
    def set_get_offline_serving_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("offline", response, error_code)

    def set_get_distribution_manager_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("distribution", response, error_code)

    def set_get_analytics_engine_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("analytics", response, error_code)

    def set_get_metrics_gateway_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("metrics", response, error_code)

    def set_get_features_operator_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("features", response, error_code)

    def set_get_hosting_gateway_url_response(
        self,
        response: Optional[ServiceLocationDescriptor],
        error_code: grpc.StatusCode = grpc.StatusCode.NOT_FOUND,
    ):
        self._set_mock("hosting", response, error_code)

    def GetOfflineServingUrl(self, request, context):
        return self._handle("offline", context)

    def GetDistributionManagerUrl(self, request, context):
        return self._handle("distribution", context)

    def GetAnalyticsEngineUrl(self, request, context):
        return self._handle("analytics", context)

    def GetMetricsGatewayUrl(self, request, context):
        return self._handle("metrics", context)

    def GetFeaturesOperatorUrl(self, request, context):
        return self._handle("features", context)

    def GetHostingGatewayUrl(self, request, context):
        return self._handle("hosting", context)
