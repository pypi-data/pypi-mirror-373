from typing import List, Optional

import grpc
from _qwak_proto.qwak.vectors.v1.filters_pb2 import Filter as ProtoFilter
from _qwak_proto.qwak.vectors.v1.vector_pb2 import (
    DoubleVector,
    SearchResult,
    StoredVector,
    VectorIdentifier,
)
from _qwak_proto.qwak.vectors.v1.vector_service_pb2 import (
    DeleteVectorsRequest,
    FetchVectorRequest,
    SearchSimilarVectorsRequest,
    UpsertVectorsRequest,
)
from _qwak_proto.qwak.vectors.v1.vector_service_pb2_grpc import VectorServiceStub
from qwak.clients._inner.edge_communications import get_endpoint_url
from qwak.exceptions import QwakException, QwakNotFoundException
from qwak.inner.tool.grpc.grpc_tools import create_grpc_channel
from typeguard import typechecked


class VectorServingClient:
    def __init__(
        self,
        edge_services_url: Optional[str] = None,
        environment_id: Optional[str] = None,
    ):
        edge_services_url = get_endpoint_url(edge_services_url, environment_id)
        self._edge_services_url = edge_services_url

        grpc_channel = create_grpc_channel(
            url=edge_services_url,
            enable_ssl=False if edge_services_url.startswith("localhost") else True,
            status_for_retry=(
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.INTERNAL,
            ),
            backoff_options={"init_backoff_ms": 250},
        )

        self._vector_serving_service = VectorServiceStub(grpc_channel)

    @typechecked
    def search(
        self,
        collection_name: str,
        vector: List[float],
        properties: List[str],
        top_results: int = 1,
        include_id: bool = True,
        include_vector: bool = False,
        include_distance: bool = False,
        filters: Optional[ProtoFilter] = None,
        tenant_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for similar vectors
        """
        request: SearchSimilarVectorsRequest
        if tenant_id is not None:
            request = SearchSimilarVectorsRequest(
                collection_name=collection_name,
                reference_vector=DoubleVector(element=vector),
                properties=properties,
                max_results=top_results,
                filter=filters,
                include_id=include_id,
                include_vector=include_vector,
                include_distance=include_distance,
                tenant_id=tenant_id,
            )
        else:
            request = SearchSimilarVectorsRequest(
                collection_name=collection_name,
                reference_vector=DoubleVector(element=vector),
                properties=properties,
                max_results=top_results,
                filter=filters,
                include_id=include_id,
                include_vector=include_vector,
                include_distance=include_distance,
            )

        try:
            return list(
                self._vector_serving_service.SearchSimilarVectors(
                    request
                ).search_results
            )

        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to query collection '{collection_name}' for vector '{str(vector)}': {repr(e)}"
            )

    @typechecked
    def upsert_vectors(self, collection_name: str, vectors: List[StoredVector]) -> None:
        """
        Upsert vectors to a collection
        """
        try:
            self._vector_serving_service.UpsertVectors(
                UpsertVectorsRequest(
                    collection_name=collection_name,
                    vector=vectors,
                )
            )

        except grpc.RpcError as e:
            raise QwakException(f"Failed to upsert, got: {repr(e)}")

    @typechecked
    def delete_vectors(
        self, collection_name: str, vector_identifiers: List[VectorIdentifier]
    ) -> int:
        """
        Delete vectors from a collection
        """
        try:
            return self._vector_serving_service.DeleteVectors(
                DeleteVectorsRequest(
                    collection_name=collection_name,
                    vector_identifiers=vector_identifiers,
                )
            ).num_vectors_deleted

        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to delete vectors by id '{str(vector_identifiers)}': {repr(e)}"
            )

    @typechecked
    def fetch_vector(
        self, collection_name: str, vector_identifier: VectorIdentifier
    ) -> StoredVector:
        """
        Fetch a vector from a collection
        """
        try:
            return self._vector_serving_service.FetchVector(
                FetchVectorRequest(
                    collection_name=collection_name, vector_identifier=vector_identifier
                )
            ).vector

        except grpc.RpcError as e:
            if e.args[0].code.name == "NOT_FOUND":
                raise QwakNotFoundException(
                    f"Could not find vector {repr(vector_identifier)} in collection {collection_name}"
                )
            raise QwakException(
                f"Failed to get vector by ID '{vector_identifier}': {repr(e)}"
            )
