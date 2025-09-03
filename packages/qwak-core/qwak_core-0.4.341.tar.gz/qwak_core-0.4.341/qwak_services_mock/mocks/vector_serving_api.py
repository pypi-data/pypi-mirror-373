from dataclasses import dataclass
from typing import Dict, List

import grpc
from _qwak_proto.qwak.vectors.v1.vector_pb2 import (
    DoubleVector,
    Property,
    SearchResult,
    StoredVector,
    VectorIdentifier,
)
from _qwak_proto.qwak.vectors.v1.vector_service_pb2 import (
    DeleteVectorsResponse,
    FetchVectorRequest,
    FetchVectorResponse,
    SearchSimilarVectorsRequest,
    SearchSimilarVectorsResponse,
    UpsertVectorsRequest,
    UpsertVectorsResponse,
)
from _qwak_proto.qwak.vectors.v1.vector_service_pb2_grpc import VectorServiceServicer
from numpy import dot
from numpy.linalg import norm


@dataclass
class VectorObject:
    id: str
    vector: List[float]
    property: List[Property]


class VectorServingServiceMock(VectorServiceServicer):
    def __init__(self):
        self._vector_collections: Dict[str, Dict] = dict()

    def reset_vector_store(self) -> None:
        self._vector_collections.clear()

    def get_num_of_vectors(self, collection_name: str) -> int:
        if collection_name not in self._vector_collections:
            return 0

        return len(self._vector_collections[collection_name].values())

    def create_collection(self, collection_name: str) -> None:
        self._vector_collections[collection_name] = dict()

    def get_vector_by_ids(
        self, collection_name: str, vector_ids: List[str]
    ) -> List[dict]:
        if collection_name not in self._vector_collections:
            raise ValueError(f"Collection named {collection_name} doesn't exist")

        collection = self._vector_collections[collection_name]
        return [collection.get(_id) for _id in vector_ids if _id in collection]

    def SearchSimilarVectors(self, request: SearchSimilarVectorsRequest, context):
        if request.collection_name not in self._vector_collections:
            context.set_details(f"Collection named {request.collection} doesn't exist'")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        reference_vector = list(request.reference_vector.element)
        collection_store = self._vector_collections.get(request.collection_name, dict())

        # a naive impl of a "vector similarity" search - compute pairwise cosine distance on
        # the entire set and return top results
        result_set = sorted(
            collection_store.values(),
            key=lambda b: _cos_sim(reference_vector, b["vector"]),
        )[-request.max_results :]

        return SearchSimilarVectorsResponse(
            search_results=[
                SearchResult(
                    id=result["id"] if request.include_id else None,
                    properties=[
                        p
                        for p in result_set[0]["properties"]
                        if p.name in request.properties
                    ],
                    vector=DoubleVector(element=result["vector"])
                    if request.include_vector
                    else None,
                    distance=_cos_sim(reference_vector, result["vector"])
                    if request.include_distance
                    else None,
                )
                for result in result_set
            ]
        )

    def UpsertVectors(self, request: UpsertVectorsRequest, context):
        collection_store = self._vector_collections.get(request.collection_name, dict())
        for stored_vector in request.vector:
            id = stored_vector.vector_identifier.vector_id
            collection_store[id] = {
                "id": id,
                "vector": list(stored_vector.vector.element),
                "properties": stored_vector.properties,
            }

        self._vector_collections[request.collection_name] = collection_store
        return UpsertVectorsResponse()

    def DeleteVectors(self, request, context):
        if request.collection_name not in self._vector_collections:
            context.set_details(
                f"Collection named {request.collection_name} doesn't exist'"
            )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        collection_store = self._vector_collections[request.collection_name]
        ids_in_collection = [
            vector_identifier.vector_id
            for vector_identifier in request.vector_identifiers
            if vector_identifier.vector_id in collection_store
        ]
        for id in ids_in_collection:
            collection_store.pop(id)

        self._vector_collections[request.collection_name] = collection_store
        return DeleteVectorsResponse(num_vectors_deleted=len(ids_in_collection))

    def FetchVector(self, request, context):
        if request.collection_name not in self._vector_collections:
            context.set_details(
                f"Collection named {request.collection_name} doesn't exist'"
            )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        collection_store = self._vector_collections[request.collection_name]
        vector_identifier = request.vector_identifier
        vector_id = vector_identifier.vector_id
        if vector_id not in collection_store:
            context.set_details(f"Vector with id {vector_id} doesn't exist'")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        stored_vector_dict = collection_store[vector_id]
        return FetchVectorResponse(
            vector=StoredVector(
                vector_identifier=request.vector_identifier,
                vector=DoubleVector(element=stored_vector_dict["vector"]),
                properties=stored_vector_dict["properties"],
            )
        )


def _cos_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))
