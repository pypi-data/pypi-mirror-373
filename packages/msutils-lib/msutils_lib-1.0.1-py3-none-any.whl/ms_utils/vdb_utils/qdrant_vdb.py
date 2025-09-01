"""
Author: Gérome FERRAND
Data scientist / ML Engineer @ FreePro

"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    PointStruct,
    ScoredPoint,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from ms_utils.communication_utils import MicroServiceWs
from ms_utils.logging_lib import Logger
from ms_utils.vdb_utils._vdb_manager import VectorDBManager

logger = Logger.setup_logger(__name__, level=logging.INFO)  # logging.DEBUG
logger.propagate = False
# suppress chroma http requests info level logs
logging.getLogger("httpx").setLevel(logging.WARNING)


# distance mapper
DISTANCES = {
    "L1": Distance.MANHATTAN,
    "L2": Distance.EUCLID,
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
}

# sparse model mapper
SPARSE_MODELS = {
    "BM25": "Qdrant/bm25",
    "BM42": "Qdrant/bm42-all-minilm-l6-v2-attentions",
    "SPLADE": "prithivida/Splade_PP_en_v1",
}

# sparse model mapper
DENSE_MODELS_DIMS = {
    "BAAI/bge-m3": 1024,
}


class QdrantVdbManager(VectorDBManager):
    """Manage interaction with qdrant vdb for encoding and retrieval.

    Args:
        dense_model_name:
        sparse_model_name:
        distance:
        websocket:
        normalize:
    """

    def __init__(
        self,
        host: str,
        dense_model_name: str = "BAAI/bge-m3",
        sparse_model_name: str = "BM25",
        distance: str = "L2",
        websocket: MicroServiceWs = None,
        normalize: bool = False,
    ):
        self.dense_model_name = dense_model_name
        self.sparse_model_name = sparse_model_name
        self.normalize = normalize

        self.websocket = websocket

        self.chunks_queue = asyncio.Queue()

        self.collections = {}

        # api key used only in corp env
        self.client = QdrantClient(
            url=host,
            api_key=os.getenv("QDRANT_API_KEY") or "",
            prefer_grpc=True,
        )

        logger.info(f"Connected to {host} qdrant host")

        self.embeddings_dimensions = DENSE_MODELS_DIMS.get(dense_model_name)
        self.sparse_model = SparseTextEmbedding(
            model_name=SPARSE_MODELS[sparse_model_name]
        )

        self.distance = distance

    async def put_chunk(self, chunk):
        await self.chunks_queue.put(chunk)

    def set_dense_model_name(self, model_name: str):
        self.dense_model_name = model_name

    def set_sparse_model_name(self, model_name: str):
        self.sparse_model_name = model_name

    def set_distance(self, distance: str):
        self.distance = distance

    def set_normalize(self, normalize: bool):
        self.normalize = normalize

    def set_websocket(self, websocket: MicroServiceWs):
        """
        websocket setter
        Args:
            websocket: the websocket
        """
        self.websocket = websocket

    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection already exists in chroma instance.

        :param collection_name: The name of the collection to create or to get.
        :return: True if the collection exists.
        """
        return self.client.collection_exists(collection_name=collection_name)

    def get_collection(
        self,
        collection_names: List[str],
    ) -> Dict:
        """Read a collection (if it exists already).

        :param collection_names: The name of the collection to get.
        """
        for collection_name in collection_names:
            if self.collection_exists(collection_name):
                self.collections[collection_name] = self.client.get_collection(
                    collection_name
                )
            else:
                self.collections[collection_name] = None

        return self.collections

    def create_collection(
        self,
        collection_name: str,
        hybrid_search: bool = True,
        # hybrid_search_params: Dict= None
    ) -> None:
        """Create a new empty collection.

        Args:
            collection_name: The name of the collection to create
            hybrid_search: enable hybrid search
            # hybrid_search_params: parameters associated with hybrid search
        """
        if hybrid_search:
            self._create_hybrid_collection(collection_name)
        else:
            # for now, let's start only with a hybrid collection,
            # even by default

            # self.create_standard_collection()
            self._create_hybrid_collection(collection_name)

    def _create_standard_collection(self, collection_name: str):
        """
        Instantiate a standard collection
        Args:
            collection_name: the name of the instantiated collection
        """
        raise NotImplementedError

    def _create_hybrid_collection(self, collection_name: str) -> None:
        """
        Instantiate a hybrid collection
        Args:
            collection_name: the name of the instantiated collection
        """
        if self.collection_exists(collection_name):
            self.get_collection([collection_name])
        else:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "text-dense": VectorParams(
                        size=self.embeddings_dimensions,
                        distance=DISTANCES[self.distance],
                    )
                },
                sparse_vectors_config={
                    "text-sparse": SparseVectorParams(
                        index=SparseIndexParams(on_disk=False)
                    )
                },
            )

    def delete_collection(self, collection_names: List[str]) -> None:
        """Delete one or more collections.

        :param collection_names: The name of the collection(s) to delete.
        """
        for collection_name in collection_names:
            self.client.delete_collection(collection_name=collection_name)

    def _encode_sparse(self, texts: List[str]) -> List[Dict]:
        """
        Encode the given text with a sparse model.
        Args:
            texts: the text to encode sparsely

        Returns:
            the list of text sparse embeddings (with the same indices)
        """
        embeddings = [
            SparseVector(
                indices=sv.indices.tolist(), values=sv.values.tolist()
            )
            for i, sv in enumerate(
                self.sparse_model.embed(texts, batch_size=32)
            )
        ]

        return embeddings

    def update(
        self,
        collection_name: str,
        dense_vectors: List[List[float]],
        docs: list[str] = None,
        sparse_vectors: List[float] = None,
        ids: list[str | int] = None,
        metadatas: list[dict] = None,
    ) -> list[str | int]:
        """Update an object content based on its textual content in the named collection.
        /!\ use self.insert(), so it will recompute above None parameters (though docs)

        Args:
          collection_name: the name of the collection within which the
          dense_vectors: dense embeddings of the given documents
          sparse_vectors: sparse embeddings of the given documents
          insertion has to be done
          docs: documents to store
          ids: documents indices. Can be set to offer a better way to
          manage the DB.
          metadatas: set of metadata to add to each document

        Returns:
            the id list of the updated documents

        """
        return self.insert(
            collection_name=collection_name,
            docs=docs,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
            ids=ids,
            metadatas=metadatas,
        )

    def insert(
        self,
        collection_name: str,
        docs: List[str],
        dense_vectors: List[List[float]],
        sparse_vectors: List[List[float]] = None,
        ids: list[str | int] = None,
        metadatas: list[dict] = None,
    ) -> list[str | int]:
        """Insert a set of data into the named collection.

        Args:
          collection_name: the name of the collection within which the
          insertion has to be done
          docs: documents to store
          dense_vectors: dense embeddings of the given documents
          sparse_vectors: sparse embeddings of the given documents
          ids: documents indices. Can be set to offer a better way to
          manage the DB.
          metadatas: set of metadata to add to each document

        Returns:
            the id list of the inserted documents
        """
        if sparse_vectors is None:
            sparse_vectors = self._encode_sparse(docs)

        if ids is None:
            ids = [
                str(uuid.uuid5(uuid.NAMESPACE_DNS, str(doc))) for doc in docs
            ]

        if metadatas is None:
            metadatas = [{}] * max(
                len(ids), len(docs), len(dense_vectors), len(sparse_vectors)
            )

        points = []
        for indice, doc, dense_vector, sparse_vector, metadata in zip(
            ids, docs, dense_vectors, sparse_vectors, metadatas
        ):
            point = PointStruct(
                id=indice,
                vector={
                    "text-dense": dense_vector,
                    "text-sparse": sparse_vector,
                },
                payload={
                    "text": doc,
                    "collection_name": collection_name,
                    "dense_encoder": self.dense_model_name,
                    "sparse_encoder": self.sparse_model_name,
                    "norm": "L2" if self.normalize else False,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    **metadata,
                },
            )
            points.append(point)
        self.client.upsert(collection_name=collection_name, points=points)

        return ids

    def delete_document(
        self, collection_name: str, doc_ids: List[str] | str
    ) -> None:
        """Delete the objects referenced by the given ids.

        Args:
          collection_name: the name of the collection within which the
          deletion has to be done
          doc_ids: the ids of the object to delete
        """
        self.client.delete(
            collection_name=collection_name, points_selector=doc_ids
        )

    def get_document(
        self, collection_name: str, doc_ids: List[str] | str
    ) -> List[Any]:
        """Retrieve the objects referenced by the given ids.

        Args:
          collection_name: the name of the collection within which the
          retrieving has to be done
          doc_ids: the ids of the objects to retrieve

        Returns:
            the list of the documents to retrieve
        """
        return self.client.retrieve(
            collection_name=collection_name,
            ids=doc_ids if isinstance(doc_ids, List) else [doc_ids],
        )

    def get_emb_model(self, collection_names: List[str]) -> List[str]:
        """
        Get the embedding models used in the given collection name.
        Args:
            collection_names: the name of the collection to request.

        Returns:
            the list of the embedding model used in the given collection name.
        """
        try:
            return self.get_dense_emb_model(
                collection_names
            ) + self.get_sparse_emb_model(collection_names)
        except KeyError as e:
            logger.error(f"Metadata or encoding model are unknown: {e}")
            raise

    def get_dense_emb_model(self, collection_names: List[str]) -> List[str]:
        """
        Get the dense embedding model used in the given collection name.
        Args:
            collection_names: the name of the collection to request.

        Returns:
            the list of the embedding model used in the given collection name.
        """
        try:
            return [
                self.client.scroll(collection_name=collection_name, limit=1)[
                    0
                ][0].payload["dense_encoder"]
                for collection_name in collection_names
            ]
        except KeyError as e:
            logger.error(f"Metadata or encoding model are unknown: {e}")
            raise

    def get_sparse_emb_model(self, collection_names: List[str]) -> List[str]:
        """
        Get the sparse embedding model used in the given collection name.
        Args:
            collection_names: the name of the collection to request.

        Returns:
            the list of the embedding model used in the given collection name.
        """
        try:
            return [
                self.client.scroll(collection_name=collection_name, limit=1)[
                    0
                ][0].payload["sparse_encoder"]
                for collection_name in collection_names
            ]
        except KeyError as e:
            logger.error(f"Metadata or encoding model are unknown: {e}")
            raise

    def get_norm(self, collection_names: List[str]) -> List[str]:
        """
        Get the normalization method used for all the document embeddings of the given collection name.
        Args:
            collection_names: the name of the collection to request.

        Returns:
            The list of the normalization method used for all documents of the given collection name.
        """
        try:
            return [
                self.client.scroll(collection_name=collection_name, limit=1)[
                    0
                ][0].payload["norm"]
                for collection_name in collection_names
            ]
        except KeyError as e:
            logger.error(f"Metadata or norm are unknown: {e}")
            raise

    @staticmethod
    def reciprocal_rank_fusion(
        rank_lists: List[List[Dict]],
        top_k: int = 10,
        alpha: int = 60,
        beta: float = 0.6,
    ) -> List[Dict]:
        """
        Custom implementation of Reciprocal Rank Fusion for hybrid search,
         with weighted Sparse-Dense Ranking.
        Args:
            rank_lists: list of the ranked docs
            (ie: with the form [[doc_d_1, ..., doc_d_k], [doc_s_1, ..., doc_s_k]])
            top_k: the number of docs to retrieve.
            alpha: The constant alpha reduces the impact of high rankings. 6O kept from the original method.
            (cf. see constant k in original paper: https://doi.org/10.1145/1571941.1572114)
            beta: the weight of the dense retrieval impact,
            knowing that the weight of the sparse impact is (1 - beta)

        Returns: the merged and re-ranked list of documents

        """
        if not (0 <= beta <= 1):
            raise ValueError("beta should be between 0 and 1")

        all_ids = set(
            item["id"] for rank_list in rank_lists for item in rank_list
        )
        id_to_index = {doc_id: idx for idx, doc_id in enumerate(all_ids)}

        default_rank = float("inf")
        rank_matrix = np.full((len(all_ids), len(rank_lists)), default_rank)

        for list_idx, rank_list in enumerate(rank_lists):
            for i, rank_entry in enumerate(rank_list):
                doc_id = rank_entry["id"]
                rank = i + 1
                rank_matrix[id_to_index[doc_id], list_idx] = rank

        # dense weight = beta | sparse weight = (1 - beta)
        weights = np.array([beta, 1 - beta])[: len(rank_lists)]
        rrf_scores = np.sum(weights * (1.0 / (alpha + rank_matrix)), axis=1)

        sorted_indices = np.argsort(-rrf_scores)
        sorted_items = [
            (list(id_to_index.keys())[idx], rrf_scores[idx])
            for idx in sorted_indices
        ]

        final_results = [
            {"id": doc_id, "combined_score": score}
            for doc_id, score in sorted_items[:top_k]
        ]
        return final_results

    def query(
        self,
        collection_name: str,
        query: str,
        query_emb: List[float],
        top_k: int = 10,
        beta: float = 0.7,
        max_distance: float = None,
    ) -> List[Dict]:
        """
        Query the given collection to get the closest semantically documents according to the given query.
        Args:
            collection_name: the collection to request.
            query: the query used to retrieve the closest semantically
            query_emb: the embedding of the query
            top_k: the number of documents to retrieve
            beta: the weight of the dense retrieval impact,
            knowing that the weight of the sparse impact is (1 - beta)
            max_distance: the maximum distance to consider for the query for dense search

        Returns:
            the list of relevant doc according to the query and the other parameters
        """
        query_dense_vector = query_emb
        query_sparse_vector = self._encode_sparse([query])[0]

        dense_results = self.client.search(
            collection_name=collection_name,
            query_vector=("text-dense", query_dense_vector),
            limit=top_k,
        )
        sparse_results = self.client.query_points(
            collection_name=collection_name,
            query=query_sparse_vector,
            using="text-sparse",
            limit=top_k,
        ).points

        # minimize data
        dense_scores = [
            {"id": res.id, "score": res.score} for res in dense_results
        ]
        sparse_scores = [
            {"id": res.id, "score": res.score} for res in sparse_results
        ]

        if beta == 1 and max_distance is not None:
            dense_scores = [
                score
                for score in dense_scores
                if score["score"] <= max_distance
            ]
            # otherwise rrf will give 0 to sparse results and still return them
            sparse_scores = []

        ranked_results = self.reciprocal_rank_fusion(
            rank_lists=[dense_scores, sparse_scores], top_k=top_k, beta=beta
        )

        # remapping
        id_to_object = {obj.id: obj for obj in dense_results + sparse_results}
        final_results = [id_to_object[item["id"]] for item in ranked_results]
        final_results = [
            EnrichedScoredPoint(p, custom_attr="dense_score")
            for p in final_results
        ]
        for item, rank, dense in zip(
            final_results, ranked_results, dense_scores
        ):
            if item.id == rank["id"]:
                item.score = float(rank["combined_score"])
            if item.id == dense["id"]:
                item.dense_score = float(dense["score"])

        return final_results


class EnrichedScoredPoint:
    def __init__(self, point: ScoredPoint, custom_attr: Optional[str] = None):
        self._point = point
        self.dense_score = custom_attr

    def __getattr__(self, name):
        return getattr(self._point, name)

    def dict(self):
        return {
            "id": self.id,
            "version": self.version,
            "score": self.score,
            "payload": self.payload,
            "vector": self.vector,
            "dense_score": self.dense_score,
        }
