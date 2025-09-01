"""
Author: Gérome FERRAND
Data scientist / ML Engineer @ FreePro

"""

from abc import ABC, abstractmethod
from typing import Any, List


class VectorDBManager(ABC):
    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection already exists in chroma instance.

        :param collection_name: The name of the collection to create or to get.
        :return: True if the collection exists.
        """

    @abstractmethod
    def get_collection(
        self,
        collection_names: List[str],
    ) -> None:
        """Read a collection (if it exists already).

        :param collection_names: The name of the collection to get.
        """

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        hybrid_search: bool = True,
    ) -> None:
        """Create a new empty collection.

        Args:
            collection_name: The name of the collection to create
            hybrid_search: enable hybrid search
            # hybrid_search_params: parameters associated with hybrid search
        """

    @abstractmethod
    def delete_collection(self, collection_names: List[str]) -> None:
        """Delete one or more collections.

        :param collection_names: The name of the collection(s) to delete.
        """

    @abstractmethod
    def update(
        self,
        collection_name: str,
        doc_id: str,
        embs: list[Any | list[Any] | list[float]],
        ids: list[str | int] = None,
        docs: list[Any | list[Any] | list[str]] = None,
        metadatas: list[dict] = None,
    ) -> None:
        """Update an object content based on its id in the named collection.

        Args:
          collection_name: the name of the collection within which the
          update has to be done
          doc_id: the id of the object to update
          embs: documents embeddings to store
          ids: documents indices, can be set to offer a better way to
          manage the DB
          docs: documents to store
          metadatas: documents metadatas (can contain what you want as dict)
        """

    @abstractmethod
    def insert(
        self,
        collection_name: str,
        docs: List[str],
        dense_vectors: List[List[float]],
        sparse_vectors: List[List[float]] = None,
        ids: list[str | int] = None,
        metadatas: list[dict] = None,
    ) -> None:
        """Insert a set of data into the named collection.

        Args:
          collection_name: the name of the collection within which the
          insertion has to be done
          dense_vectors: dense embeddings of the given documents
          sparse_vectors: sparse embeddings of the given documents
          docs: documents to store
          ids: documents indices. Can be set to offer a better way to
          manage the DB.
          metadatas: documents metadatas (can contain what you want as dict)
        """

    @abstractmethod
    def delete_document(self, collection_name: str, doc_id: str) -> None:
        """Delete the object referenced by the given id.

        Args:
          collection_name: the name of the collection within which the
          deletion has to be done
          doc_id: the id of the object to delete
        """

    @abstractmethod
    def query(
        self,
        collection_name: str,
        query: str,
        query_emb: List[float],
        top_k: int = 10,
        beta: float = 0.7,
    ) -> dict:
        """
        Query the given collection to get the closest semantically documents according to the given query.
        Args:
            collection_name: the collection to request.
            query: the query used to retrieve the closest semantically
            query_emb: the embedding of the query
            top_k: the number of documents to retrieve
            beta: the weight of the dense retrieval impact,
            knowing that the weight of the sparse impact is (1 - beta)

        Returns:
            the list of relevant doc according to the query and the other parameters
        """
