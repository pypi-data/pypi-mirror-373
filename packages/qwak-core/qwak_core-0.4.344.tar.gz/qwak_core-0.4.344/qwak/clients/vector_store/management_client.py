from typing import List, Optional

import grpc
from _qwak_proto.qwak.vectors.v1.collection.collection_pb2 import (
    VectorCollection,
    VectorCollectionMetric,
    VectorCollectionSpec,
    VectorCollectionVectorizer,
)
from _qwak_proto.qwak.vectors.v1.collection.collection_service_pb2 import (
    CreateCollectionRequest,
    DeleteCollectionByIdRequest,
    DeleteCollectionByNameRequest,
    GetCollectionByIdRequest,
    GetCollectionByNameRequest,
    ListCollectionsRequest,
)
from _qwak_proto.qwak.vectors.v1.collection.collection_service_pb2_grpc import (
    VectorCollectionServiceStub,
)
from dependency_injector.wiring import Provide, inject
from qwak.exceptions import QwakException
from qwak.inner.di_configuration import QwakContainer


class VectorManagementClient:
    @inject
    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
        self._vector_management_service: VectorCollectionServiceStub = (
            VectorCollectionServiceStub(grpc_channel)
        )

    def create_collection(
        self,
        name: str,
        dimension: int,
        description: str = None,
        metric: VectorCollectionMetric = VectorCollectionMetric.COLLECTION_METRIC_L2_SQUARED,
        vectorizer: Optional[str] = None,
        multi_tenant: bool = False,
    ) -> VectorCollection:
        """
        Create a collection
        """
        try:
            return self._vector_management_service.CreateCollection(
                CreateCollectionRequest(
                    collection_spec=VectorCollectionSpec(
                        name=name,
                        description=description,
                        vectorizer=VectorCollectionVectorizer(
                            qwak_model_name=vectorizer
                        ),
                        metric=metric,
                        dimension=dimension,
                        multi_tenancy_enabled=multi_tenant,
                    )
                )
            ).vector_collection

        except grpc.RpcError as e:
            raise QwakException(f"Failed to create collection: {e.details()}")

    def list_collections(self) -> List[VectorCollection]:
        """
        List all vector collections
        """
        try:
            return self._vector_management_service.ListCollections(
                ListCollectionsRequest()
            ).vector_collections

        except grpc.RpcError as e:
            raise QwakException(f"Failed to list collections: {e.details()}")

    def get_collection_by_name(self, name: str) -> VectorCollection:
        """
        Get vector collection by name
        """
        try:
            return self._vector_management_service.GetCollectionByName(
                GetCollectionByNameRequest(name=name)
            ).vector_collection
        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to get collection by name '{name}': {e.details()}"
            )

    def get_collection_by_id(self, id: str) -> VectorCollection:
        """
        Get vector collection by id
        """
        try:
            return self._vector_management_service.GetCollectionById(
                GetCollectionByIdRequest(id=id)
            ).vector_collection
        except grpc.RpcError as e:
            raise QwakException(f"Failed to get collection by id '{id}': {e.details()}")

    def delete_collection_by_id(self, id: str) -> None:
        """
        Delete vector collection by id
        """
        try:
            self._vector_management_service.DeleteCollectionById(
                DeleteCollectionByIdRequest(id=id)
            )
        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to delete collection by id '{id}': {e.details()}"
            )

    def delete_collection_by_name(self, name: str) -> None:
        """
        Delete vector collection by id
        """
        try:
            self._vector_management_service.DeleteCollectionByName(
                DeleteCollectionByNameRequest(name=name)
            )
        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to delete collection by name '{name}': {e.details()}"
            )
