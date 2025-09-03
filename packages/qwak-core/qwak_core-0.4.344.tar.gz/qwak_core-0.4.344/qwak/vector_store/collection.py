import re
from dataclasses import dataclass
from typing import Dict, List, Optional, TypeVar, Union

from _qwak_proto.qwak.vectors.v1.vector_pb2 import (
    Property,
    SearchResult as ProtoSearchResult,
    StoredVector as ProtoStoredVector,
    VectorIdentifier as ProtoVectorIdentifier,
)
from qwak.clients.vector_store.serving_client import VectorServingClient
from qwak.exceptions import QwakException
from qwak.vector_store.filters import Filter
from qwak.vector_store.inference_client import VectorStoreInferenceClient
from qwak.vector_store.utils.upsert_utils import (
    _divide_chunks,
    _upsert_natural_input,
    _upsert_vectors,
)
from typeguard import typechecked

NaturalInput = TypeVar("T")
NaturalInputs = List[NaturalInput]
Vector = List[float]
Properties = Dict[str, Union[str, int, bool, float]]

_TENANT_ID_PATTERN = r"^[a-zA-Z0-9_-]{4,64}$"


@dataclass
class SearchResult:
    """
    A class used to represent the result of a vector similarity search operation.

     Attributes:
         properties (dict): The dictionary of properties to attach with the vectors
         id (str): The vector object unique identifier
         vector (Vector): The vector values
         distance (int): The distance metric indicating how similar the vector is to the search query.
             Smaller values indicate higher similarity.
    """

    properties: Properties
    id: Optional[str]
    vector: Optional[Vector]
    distance: Optional[float]


class Collection:
    """
    The Collection class is a Python class that provides functionalities for handling operations on vectors within a
    specific collection in a vector store. This class should be used after a collection has been created or fetched
    using `VectorStoreClient`.

    The Collection class allows you to:
        * **Search for Similar Vectors**: This helps in finding vectors that are most similar to a given query vector.
        * **Upsert Vectors**: This operation allows you to insert new vectors into the collection or update existing
            vectors if they already exist.
        * **Delete Vectors by ID**: This operation deletes vectors based on their unique identifiers
    """

    id: str
    name: str
    metric: str
    dimension: int
    description: Optional[str]
    vectorizer: Optional[str]
    multi_tenant: bool

    _vector_serving_client: VectorServingClient
    _type_to_proto_property_mapping: Dict[str, TypeVar] = {
        str: "string_val",
        bool: "bool_val",
        int: "int_val",
        float: "double_val",
    }

    _proto_property_to_type_mapping = {
        v: k for k, v in _type_to_proto_property_mapping.items()
    }

    def __init__(
        self,
        id: str,
        name: str,
        metric: str,
        dimension: int,
        vector_serving_client: VectorServingClient,
        description: Optional[str] = None,
        vectorizer: Optional[str] = None,
        muli_tenant: bool = False,
    ):
        """
        Initializes a `Collection` client object to interact with Qwak's vector serving service. Should not be created
        directly - created or fetched using the `VectorStoreClient` object.
        """
        self.id = id
        self.name = name
        self.description = description
        self.metric = metric
        self.dimension = dimension
        self.vectorizer = vectorizer
        self._vector_serving_client = vector_serving_client
        self._realtime_inference_client = None
        self.multi_tenant = muli_tenant

        if vectorizer:
            self._realtime_inference_client = VectorStoreInferenceClient(
                model_id=self.vectorizer.lower().replace(" ", "_").replace("-", "_")
            )

    @typechecked
    def search(
        self,
        output_properties: List[str],
        vector: Optional[Vector] = None,
        natural_input: Optional[NaturalInput] = None,
        top_results: int = 1,
        include_id: bool = True,
        include_vector: bool = False,
        include_distance: bool = False,
        filter: Optional[Filter] = None,
        tenant_id: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Searches for vectors in the collection that are most similar to a given query vector.
        Vector similarity is a measure of the closeness or similarity between two vectors. In the context of machine
        learning, vectors often represent points in a high-dimensional space, and the concept of similarity between
        vectors can be crucial for many tasks such as clustering, classification, and nearest-neighbor searches.

        Parameters:
            output_properties (list): A list of property fields to include in the results.
            vector (list): The vector to get the most similar vectors to according to the distance metric
            natural_input (any): Natural inputs (text, image) which should be embedded by the collection and, and
              according to the resulting embedding - get the most similar vectors
            top_results (int): The number of relevant results to return
            include_id (list): Whether to include the vector ID's in the result set
            include_vector (list): Whether to include the vector values themselves in the result set
            include_distance (list): Whether to include the distance calculations to the result set
            filter (Filter): Pre-filtering search results
            tenant_id (str): tenant ID, passed if and only if the collection has multi tenancy enabled

        Returns:
            List[SearchResult]: A list of SearchResult object, which is used as a container for the search results

        Raises:
            QwakException: If you don't provide either vectors or natural_inputs
            QwakException: If you provide both vectors and natural_inputs
            QwakException: If the tenant provided mismatches the configuration
        """
        if not (bool(vector) ^ bool(natural_input)):
            raise QwakException(
                "Exactly one of {'vectors', 'natural_input'} should be passed"
            )

        if natural_input:
            vector = self._transform_natural_input_to_vectors(
                natural_input=natural_input
            )
        proto_filter = filter._to_proto() if filter else None
        self._validate_tenant(tenant_id)

        return [
            self._to_search_result(
                result,
                include_id=include_id,
                include_distance=include_distance,
                include_vector=include_vector,
            )
            for result in self._vector_serving_client.search(
                collection_name=self.name,
                vector=vector,
                properties=output_properties,
                top_results=top_results,
                include_id=include_id,
                include_vector=include_vector,
                include_distance=include_distance,
                filters=proto_filter,
                tenant_id=tenant_id,
            )
        ]

    @typechecked
    def upsert(
        self,
        ids: List[str],
        properties: List[Properties],
        vectors: Optional[List[Vector]] = None,
        natural_inputs: Optional[NaturalInputs] = None,
        batch_size: int = 1000,
        multiproc: bool = False,
        max_processes: Optional[int] = None,
        *,
        tenant_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Inserts new vectors into the collection or updates existing vectors. Notice that this method will overwrite
        existing vectors with the same IDs.

        Parameters:
            ids (str): A list of vector ids to be added
            vectors (list): The list of vectors to add. This attribute or `natural_inputs` must be set
            natural_inputs (list): Natural inputs (text, image) which should be embedded by the collection and added
              to the store. This attribute or `vectors` must be set
            properties (dict): A dictionary of properties to attach with the vectors
            batch_size(int): maximum batch size when upserting against the backend Vector Store, defaults to 1000
            multiproc (bool): whether to use multiprocessing, defaults to False
            max_processes (Optional[int]): max number of processes if multiproc is selected, multiproc must be enabled
            tenant_ids (List[str]): tenant ids, should be specified if and only if the collection has multi tenancy enabled.

        Raises:
            QwakException: If you don't provide either vectors or natural_inputs
            QwakException: If you provide both vectors and natural_inputs
        """

        if not (bool(vectors) ^ bool(natural_inputs)):
            raise QwakException(
                "`vectors` or `natural` inputs should be defined and not empty. But not both"
            )

        if max_processes is not None and not multiproc:
            raise QwakException("Can not set max_processes if multiproc is not enabled")

        self._validate_tenant_ids(
            vector_ids=vectors, tenant_ids=tenant_ids, verb="upserting"
        )
        id_tpls = zip(ids, tenant_ids) if self.multi_tenant else ids

        if (len(vectors or natural_inputs) != len(ids)) or (
            len(properties) != len(ids)
        ):
            raise QwakException(
                "Non matching lengths for input list (vectors / natural inputs), IDs, and properties list. "
                "Make sure all 3 fields are aligned in length"
            )
        if bool(natural_inputs):
            _upsert_natural_input(
                vector_tuples=list(zip(id_tpls, natural_inputs, properties)),
                chunk_size=batch_size,
                vectorizer_name=self.vectorizer,
                collection_name=self.name,
                edge_services_url=self._vector_serving_client._edge_services_url,
                multiproc=multiproc,
                max_processes=max_processes,
            )
        else:
            _upsert_vectors(
                vector_tuples=list(zip(id_tpls, vectors, properties)),
                chunk_size=batch_size,
                collection_name=self.name,
                edge_services_url=self._vector_serving_client._edge_services_url,
                multiproc=multiproc,
                max_processes=max_processes,
            )

    @typechecked
    def delete(
        self,
        vector_ids: List[str],
        *,
        tenant_ids: Optional[List[str]] = None,
        batch_size: int = 10000,
    ) -> int:
        """
        Deletes vectors from the collection based on their IDs.

        Parameters:
            vector_ids (list): A list of vector IDs to delete.
            batch_size (int): optional batch size, defaults to 10000
            tenant_ids (list): tenant IDs (same length as vector_ids, used only when multi tenancy is enabled)

        Returns:
            int: Number of actual vectors deleted from the collection
        """
        self._validate_tenant_ids(
            vector_ids=vector_ids, tenant_ids=tenant_ids, verb="deleting"
        )
        vector_identifiers: List[ProtoVectorIdentifier] = self._extract_tenant_ids(
            vector_ids, tenant_ids
        )

        return sum(
            self._vector_serving_client.delete_vectors(
                collection_name=self.name, vector_identifiers=ids_chunk
            )
            for ids_chunk in _divide_chunks(vector_identifiers, batch_size)
        )

    @typechecked
    def fetch(self, vector_id: str, *, tenant_id: Optional[str] = None) -> SearchResult:
        """
        Fetches a vector from the collection based on its ID.

        Parameters:
            vector_id (str): The ID of the vector to fetch.
            tenant_id (str, optional): Tenant id, passed if and only if multi tenancy is enabled

        Returns:
            SearchResult: A SearchResult object, which is used as a container for the search results
        """
        self._validate_tenant(tenant_id)
        vector_identifier: ProtoVectorIdentifier
        if tenant_id is not None:
            vector_identifier = ProtoVectorIdentifier(
                vector_id=vector_id, tenant_id=tenant_id
            )
        else:
            vector_identifier = ProtoVectorIdentifier(vector_id=vector_id)

        result = self._vector_serving_client.fetch_vector(
            collection_name=self.name, vector_identifier=vector_identifier
        )

        return self._to_search_result(
            result, include_id=True, include_distance=False, include_vector=True
        )

    def _to_search_result(
        self,
        search_result: Union[ProtoSearchResult, ProtoStoredVector],
        include_id: bool,
        include_vector: bool,
        include_distance: bool,
    ) -> SearchResult:
        id = (
            search_result.vector_identifier.vector_id
            if type(search_result) is ProtoStoredVector
            else search_result.id
        )
        return SearchResult(
            id=id if include_id else None,
            vector=(
                [e for e in search_result.vector.element] if include_vector else None
            ),
            distance=search_result.distance if include_distance else None,
            properties={
                prop.name: self._extract_value_with_type(prop)
                for prop in search_result.properties
            },
        )

    def _extract_value_with_type(self, prop: Property):
        type_caster = self._proto_property_to_type_mapping.get(
            prop.WhichOneof("value_type"), None
        )
        if not type_caster:
            raise QwakException(
                f"Cannot deserialize property with type {type(type_caster)}. This means an invalid property type"
                f" was registered to the platform. Please delete and add the vector object again."
            )

        return type_caster(getattr(prop, prop.WhichOneof("value_type")))

    def _transform_natural_input_to_vectors(
        self, natural_input: NaturalInput
    ) -> Vector:
        if not self.vectorizer:
            raise QwakException(
                "Unable to search by natural input because the collection does not have a Vectorizer defined."
            )
        return self._realtime_inference_client.get_embedding(natural_input)

    def _transform_natural_input_list_to_vectors(
        self, natural_inputs: NaturalInputs
    ) -> List[Vector]:
        return [
            self._transform_natural_input_to_vectors(natural_input=natural_input)
            for natural_input in natural_inputs
        ]

    def _validate_tenant(self, tenant_id: Optional[str] = None):
        if self.multi_tenant:
            # we are multi tenant, assert a valid tenant is passed
            if tenant_id is None:
                raise QwakException(
                    "Tenant ID must be passed when multi tenancy is enabled"
                )

            self._validate_tenant_id(tenant_id)
        else:
            if tenant_id is not None:
                raise QwakException(
                    f"Collection {self.name} is not multi tenant, can not specify tenant"
                )

    def _validate_tenant_id(self, tenant_id: str):
        if not (bool(re.match(_TENANT_ID_PATTERN, tenant_id))):
            raise QwakException(
                f"Tenant ID {tenant_id} does not conform to {_TENANT_ID_PATTERN}"
            )

    def _validate_tenant_ids(
        self, vector_ids: List[str], tenant_ids: Optional[List[str]], verb: str
    ) -> None:
        if self.multi_tenant:
            if tenant_ids is None:
                raise QwakException(
                    f"Tenant IDs must be provided when {verb} against multitenant collections"
                )
            if len(tenant_ids) != len(vector_ids):
                raise QwakException(
                    f"Got different number of vector ids {len(vector_ids)} and tenant ids {len(tenant_ids)}"
                )
            for tenant_id in tenant_ids:
                self._validate_tenant_id(tenant_id=tenant_id)
        else:
            if tenant_ids is not None:
                raise QwakException(
                    f"Collection {self.name} does not have multi tenancy enabled, do not pass tenant ids"
                )

    def _extract_tenant_ids(
        self, vector_ids: List[str], tenant_ids: Optional[List[str]]
    ) -> List[ProtoVectorIdentifier]:
        vector_identifiers: List[ProtoVectorIdentifier]
        if self.multi_tenant:
            vector_identifiers = [
                ProtoVectorIdentifier(vector_id=vector_id, tenant_id=tenant_id)
                for vector_id, tenant_id in zip(vector_ids, tenant_ids)
            ]
        else:
            vector_identifiers = [
                ProtoVectorIdentifier(vector_id=vector_id) for vector_id in vector_ids
            ]

        return vector_identifiers
