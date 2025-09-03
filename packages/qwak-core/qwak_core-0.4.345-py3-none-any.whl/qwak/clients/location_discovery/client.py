from typing import Callable

import grpc
from _qwak_proto.qwak.service_discovery.service_discovery_location_pb2 import (
    ServiceLocationDescriptor,
)
from _qwak_proto.qwak.service_discovery.service_discovery_location_service_pb2 import (
    GetServingUrlRequest as ProtoGetServingUrlRequest,
    GetServingUrlRequestResponse as ProtoGetServingUrlRequestResponse,
)
from _qwak_proto.qwak.service_discovery.service_discovery_location_service_pb2_grpc import (
    LocationDiscoveryServiceStub,
)
from dependency_injector.wiring import Provide
from qwak.exceptions import QwakException
from qwak.inner.di_configuration import QwakContainer


class LocationDiscoveryClient:
    """
    Client for querying service locations from the LocationDiscoveryService.
    """

    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
        self._service = LocationDiscoveryServiceStub(grpc_channel)

    @staticmethod
    def _get_location(
        method: Callable[
            [ProtoGetServingUrlRequest], ProtoGetServingUrlRequestResponse
        ],
    ) -> ServiceLocationDescriptor:
        """
        Calls a specific RPC and extracts the service location descriptor.

        Args:
            method: The gRPC method to call.

        Returns:
            ServiceLocationDescriptor: Contains service_url and location metadata.
        """
        try:
            request = ProtoGetServingUrlRequest()
            response = method(request)
            return response.location
        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to retrieve service location. Error is: {e.details()}"
            ) from e

    def get_offline_serving(self) -> ServiceLocationDescriptor:
        """Fetches the offline serving service location."""
        return self._get_location(self._service.GetOfflineServingUrl)

    def get_distribution_manager(self) -> ServiceLocationDescriptor:
        """Fetches the distribution manager service location."""
        return self._get_location(self._service.GetDistributionManagerUrl)

    def get_analytics_engine(self) -> ServiceLocationDescriptor:
        """Fetches the analytics engine service location."""
        return self._get_location(self._service.GetAnalyticsEngineUrl)

    def get_metrics_gateway(self) -> ServiceLocationDescriptor:
        """Fetches the metrics gateway service location."""
        return self._get_location(self._service.GetMetricsGatewayUrl)

    def get_features_operator(self) -> ServiceLocationDescriptor:
        """Fetches the features operator service location."""
        return self._get_location(self._service.GetFeaturesOperatorUrl)

    def get_hosting_gateway(self) -> ServiceLocationDescriptor:
        """Fetches the hosting gateway service location."""
        return self._get_location(self._service.GetHostingGatewayUrl)
