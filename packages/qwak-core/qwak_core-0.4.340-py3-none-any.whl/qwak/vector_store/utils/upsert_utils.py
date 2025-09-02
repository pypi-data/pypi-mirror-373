import os
from functools import partial
from math import ceil
from multiprocessing import Pool, set_start_method
from typing import Dict, Iterable, List, Optional, Tuple, TypeVar, Union

from _qwak_proto.qwak.vectors.v1.vector_pb2 import (
    DoubleVector,
    Property,
    StoredVector,
    VectorIdentifier,
)
from dependency_injector.wiring import Provide, inject
from qwak.clients.vector_store.serving_client import VectorServingClient
from qwak.exceptions import QwakException
from qwak.inner.di_configuration import QwakContainer
from qwak.vector_store.inference_client import VectorStoreInferenceClient
from typeguard import typechecked

_NaturalInput = TypeVar("T")
_NaturalInputs = List[_NaturalInput]
_Vector = List[float]
_Properties = Dict[str, Union[str, int, bool, float]]

_type_to_proto_property_mapping: Dict = {
    str: "string_val",
    bool: "bool_val",
    int: "int_val",
    float: "double_val",
}


def _build_property(key: str, value: Union[str, int, bool, float]):
    type_val = _type_to_proto_property_mapping.get(type(value), None)
    if not type_val:
        raise QwakException(
            f"Cannot upsert vector with property value type {type(value)}. "
            f"Supported types are: {list(_type_to_proto_property_mapping.keys())}"
        )

    property_args = {"name": key, type_val: value}
    return Property(**property_args)


def _rewire_qwak_container(config):
    # re-creating the container using the config from the original container.
    # note that this runs in a fresh interpreter - at that point there's a running
    # container because of the imports, but it won't necessarily have the same config
    # as the container in the parent process that spawned this one.
    # rewiring only the vector store + ecosystem and authentication - if using stuff from
    # other modules pls feel free to add it here.
    new_container = QwakContainer(config=config)
    from qwak.clients import vector_store
    from qwak.clients.administration import authentication, eco_system

    new_container.wire(
        packages=[
            authentication,
            eco_system,
            vector_store,
        ]
    )


@typechecked
def _divide_chunks(lst: List, chunk_size: int):
    if chunk_size <= 0:
        raise QwakException("Chunk size must be a positive integer")

    num_items: int = len(lst)
    num_chunks: int = ceil(num_items / chunk_size)
    for i in range(num_chunks):
        yield lst[i * chunk_size : (i + 1) * chunk_size]


def _get_vector_identifier(t: Union[str, Tuple[str, str]]):
    if type(t) is str:
        return VectorIdentifier(vector_id=t)
    return VectorIdentifier(vector_id=t[0], tenant_id=t[1])


def _upsert_vector_block(
    vector_tuples: List[Tuple[Union[str, Tuple[str, str]], _Vector, _Properties]],
    chunk_size: int,
    collection_name: str,
    edge_services_url: str,
) -> None:
    vector_serving_client: VectorServingClient = VectorServingClient(
        edge_services_url=edge_services_url
    )
    for chunk in _divide_chunks(vector_tuples, chunk_size):
        # chunk is a list of (id, vector, properties) tuples
        vector_serving_client.upsert_vectors(
            collection_name=collection_name,
            vectors=[
                StoredVector(
                    vector_identifier=_get_vector_identifier(tpl[0]),
                    vector=DoubleVector(element=tpl[1]),
                    properties=[
                        _build_property(key, value) for (key, value) in tpl[2].items()
                    ],
                )
                for tpl in chunk
            ],
        )


def _upsert_natural_input_block(
    vector_tuples: List[Tuple[VectorIdentifier, _NaturalInput, _Properties]],
    chunk_size: int,
    vectorizer_name: str,
    collection_name: str,
    edge_services_url: str,
) -> None:
    vector_serving_client: VectorServingClient = VectorServingClient(
        edge_services_url=edge_services_url
    )
    inference_client: VectorStoreInferenceClient = VectorStoreInferenceClient(
        model_id=vectorizer_name
    )
    for chunk in _divide_chunks(vector_tuples, chunk_size):
        # chunk is a list of (id, _NaturalInput, properties) tuples
        vector_serving_client.upsert_vectors(
            collection_name=collection_name,
            vectors=[
                StoredVector(
                    vector_identifier=_get_vector_identifier(tpl[0]),
                    vector=DoubleVector(
                        element=inference_client.get_embedding(natural_input=tpl[1])
                    ),
                    properties=[
                        _build_property(key, value) for (key, value) in tpl[2].items()
                    ],
                )
                for tpl in chunk
            ],
        )


@inject
def _upsert_natural_input(
    vector_tuples: List[Tuple[Union[str, Tuple[str, str]], _NaturalInput, _Properties]],
    chunk_size: int,
    vectorizer_name: str,
    collection_name: str,
    edge_services_url: str,
    multiproc: bool = False,
    max_processes: Optional[int] = None,
    config=Provide[QwakContainer.config],
):
    if not multiproc:
        _upsert_natural_input_block(
            vector_tuples=vector_tuples,
            chunk_size=chunk_size,
            vectorizer_name=vectorizer_name,
            collection_name=collection_name,
            edge_services_url=edge_services_url,
        )
    else:
        if max_processes is None:
            max_processes = os.cpu_count()
        effective_block_size: int = ceil(len(vector_tuples) / (max_processes * 4))

        f = partial(
            _upsert_natural_input_block,
            chunk_size=chunk_size,
            vectorizer_name=vectorizer_name,
            collection_name=collection_name,
            edge_services_url=edge_services_url,
        )

        blocks: Iterable[List[Tuple[str, _NaturalInput, _Properties]]] = _divide_chunks(
            vector_tuples, effective_block_size
        )
        initializer = partial(_rewire_qwak_container, config=config)
        set_start_method("spawn", force=True)

        with Pool(processes=max_processes, initializer=initializer) as p:
            p.map(f, blocks)


@inject
def _upsert_vectors(
    vector_tuples: List[Tuple[Union[str, Tuple[str, str]], _Vector, _Properties]],
    chunk_size: int,
    collection_name: str,
    edge_services_url: str,
    multiproc: bool = False,
    max_processes: Optional[int] = None,
    config=Provide[QwakContainer.config],
):
    if not multiproc:
        _upsert_vector_block(
            vector_tuples=vector_tuples,
            chunk_size=chunk_size,
            collection_name=collection_name,
            edge_services_url=edge_services_url,
        )
    else:
        if max_processes is None:
            max_processes = os.cpu_count()
        effective_block_size: int = ceil(len(vector_tuples) / (max_processes * 4))

        f = partial(
            _upsert_vector_block,
            chunk_size=chunk_size,
            collection_name=collection_name,
            edge_services_url=edge_services_url,
        )
        blocks: Iterable[List[Tuple[str, _Vector, _Properties]]] = list(
            _divide_chunks(vector_tuples, effective_block_size)
        )

        set_start_method("spawn", force=True)
        initializer = partial(_rewire_qwak_container, config=config)
        with Pool(processes=max_processes, initializer=initializer) as p:
            p.map(f, blocks)
