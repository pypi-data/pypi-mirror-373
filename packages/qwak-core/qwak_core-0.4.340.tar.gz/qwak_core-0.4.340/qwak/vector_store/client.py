from __future__ import annotations

from typing import Dict, List, Optional

from _qwak_proto.qwak.vectors.v1.collection.collection_pb2 import (
    VectorCollectionDefinition,
    VectorCollectionMetric,
)
from qwak.clients.vector_store import VectorManagementClient, VectorServingClient
from qwak.exceptions import QwakException
from qwak.vector_store.collection import Collection
from typeguard import typechecked


class VectorStoreClient:
    """
    The `VectorStoreClient` class is designed to interact with Qwak's vector store service. A vector store is a
    specialized storage service optimized for storing and querying high-dimensional vectors. These vectors can be
    representations extracted from images, text, or any other type of data.
    Vector stores are often used in machine learning applications for operations such as nearest neighbor searches,
    similarity measures, and clustering.
    """

    _vector_management_client: VectorManagementClient

    _metric_dict: Dict[str, VectorCollectionMetric] = {
        "l2_squared": VectorCollectionMetric.COLLECTION_METRIC_L2_SQUARED,
        "cosine": VectorCollectionMetric.COLLECTION_METRIC_COSINE,
        "dot_product": VectorCollectionMetric.COLLECTION_METRIC_DOT_PRODUCT,
        "l1": VectorCollectionMetric.COLLECTION_METRIC_L1,
        "hamming": VectorCollectionMetric.COLLECTION_METRIC_HAMMING,
    }

    def __init__(self, edge_services_url: Optional[str] = None):
        """
        Initializes a `VectorStoreClient` client object to interact with Qwak's vector store service
        """
        self._vector_management_client = VectorManagementClient()
        self._vector_serving_client = VectorServingClient(
            edge_services_url=edge_services_url
        )

    @typechecked
    def create_collection(
        self,
        name: str,
        dimension: int,
        description: str = None,
        metric: str = "l2_squared",
        vectorizer: Optional[str] = None,
        multi_tenant: bool = False,
    ) -> Collection:
        """
        Creates a new collection with the given name and dimension.
        Each collection in the vector store can be thought of as a table or a namespace that holds vectors of a
        particular dimension. For example, you may have a collection named "image_embeddings" where each vector is of
        dimension 512, representing an embedding of an image.

        Parameters:
            name (str): The name of the collection to create.
            dimension (int): The dimension of the vectors in the collection.
            description (str, optional): A human-readable description of the collection.
            metric (int): The distance metric used by the collection when executing similarity search
            vectorizer (str): an optional Qwak model used for vector embedding in case natural input is provided
            multi_tenant (bool): Whether this collection has multitenancy. defaults to False and cannot be changed
                                after the collection is created

        Returns:
            Collection: The Collection object which is used to interact with the vector store.

        Raises:
            QwakException: if any of the collection creation parameters are invalid
        """
        proto_definition = self._vector_management_client.create_collection(
            name=name,
            description=description,
            dimension=dimension,
            metric=self._metrics_mapper(metric),
            vectorizer=vectorizer,
            multi_tenant=multi_tenant,
        ).definition

        return self._collection_from_definition(proto_definition)

    @typechecked
    def delete_collection(self, name: str) -> None:
        """
        Deletes a collection with the given name.

        Parameters:
            name (str): The name of the collection to delete.

        Raises:
            QwakException: in case the deletion failed for any reason
        """
        self._vector_management_client.delete_collection_by_name(name=name)

    @typechecked
    def get_collection_by_name(self, name: str) -> Collection:
        """
        Fetches a collection by its name.

        Parameters:
            name (str): The name of the collection to fetch.

        Returns:
            collection: a Collection object

        Raises:
            QwakException: in case the collection doesn't exist
        """
        proto_definition = self._vector_management_client.get_collection_by_name(
            name
        ).definition
        return self._collection_from_definition(proto_definition)

    def list_collections(self) -> List[Collection]:
        """
        Lists all available collections in the current Qwak account

         Returns:
             list: A list of Collection objects.
        """
        proto_definitions = self._vector_management_client.list_collections()
        return [
            self._collection_from_definition(collection.definition)
            for collection in proto_definitions
        ]

    def _collection_from_definition(
        self, collection_definition: VectorCollectionDefinition
    ):
        return Collection(
            id=collection_definition.id,
            name=collection_definition.collection_spec.name,
            metric=collection_definition.collection_spec.metric,
            dimension=collection_definition.collection_spec.dimension,
            description=collection_definition.collection_spec.description,
            vectorizer=collection_definition.collection_spec.vectorizer.qwak_model_name,
            vector_serving_client=self._vector_serving_client,
            muli_tenant=collection_definition.collection_spec.multi_tenancy_enabled,
        )

    def _metrics_mapper(self, metric: str) -> VectorCollectionMetric:
        if metric in self._metric_dict:
            return self._metric_dict[metric]

        raise QwakException(
            f"Unsupported metric type '{metric}'. Currently supported metrics are {list(self._metric_dict.keys())}"
        )
