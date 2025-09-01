"""Reranker abstraction module"""

# pylint: disable=line-too-long

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from autorag.types.reranking import ContentWithScore
from autorag.utilities.concurrency import run_async


class Reranker(ABC):
    """
    Abstract base class for Reranker.

    This class defines the interface for reranker implementation. A reranker is
    responsible for reranking the results of the search operation done on a vector store.
    It helps in improving the relevance of retrieved documents by scoring and reordering
    them before they are passed to the generator.
    """

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Reranks the search results (documents) based on the search query

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting them based on score.

        Returns:
           List[ContentWithScore]: top_k documents ranked with decreasing reranking score.
        """
        return self._rerank(query=query, documents=documents, top_k=top_k, **kwargs)

    @abstractmethod
    def _rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Reranks the search results (documents) based on the search query

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting them based on score.

        Returns:
            List[ContentWithScore]: top_k documents ranked with decreasing reranking score.
        """
        raise NotImplementedError(  # pragma: no cover
            f"{self.__class__.__name__} does not implement '_rerank'."
        )

    async def arerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Asynchronously reranks the search results (documents) based on the search query

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting them based on score.

        Returns:
            List[ContentWithScore]: top_k documents ranked with decreasing reranking score.
        """
        return await run_async(
            lambda: self.rerank(query=query, documents=documents, top_k=top_k, **kwargs)
        )
