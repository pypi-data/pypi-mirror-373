"""Cross Encoder Reranker module implementation"""

# pylint: disable=line-too-long, duplicate-code

from typing import Any, List, Optional

from autorag.reranking.base import Reranker
from autorag.types.reranking import ContentWithScore
from autorag.utilities.logger import get_logger

logger = get_logger()


class CrossEncoderReranker(Reranker):
    """
    Cross Encoder Reranker implementation.

    This class provides an implementation of the Reranker abstract class
    using the CrossEncoder from sentence_transformer to rerank the search results.

    Example:
    .. code-block:: python

        from autorag.reranking import CrossEncoderReranker

        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        reranker = CrossEncoderReranker(
            model_name=model_name
        )
        top_k = 2
        query = "token-level interaction in retrieval"
        documents = [
                "CrossEncoder is a retrieval model that uses token-level interaction.",
                "Transformers like BERT can be used for ranking search results.",
                "This document is about machine learning and natural language processing."
            ]

        reranker.rerank(query, documents, top_k)
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the SentenceTransformer CrossEncoder model_name.

        Args:
            model_name (str, optional): Defaults to "cross-encoder/ms-marco-MiniLM-L-6-v2".
        """
        super().__init__()
        try:
            from sentence_transformers import (  # pylint: disable=import-outside-toplevel
                CrossEncoder,
            )
        except ImportError as err:
            raise ImportError(
                "Unable to locate sentence_transformers package. "
                'Please install it with `pip install "autonomize-autorag[huggingface]"`.'
            ) from err

        self._model = CrossEncoder(model_name=model_name)

    def _rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        **kwargs: Any
    ) -> List[ContentWithScore]:
        """
        Reranks the search results (documents) based on the search query and the
        loaded model_name from CrossEncoder.

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting
            them based on score.

        Returns:
            List[ContentWithScore]: top_k documents ranked with decreasing reranking score.
        """
        ranks = []
        query_pairs = [(query, document) for document in documents]
        scores = self._model.predict(query_pairs)
        scores = scores.tolist()

        ranks = [
            ContentWithScore(content=document, score=score)
            for document, score in zip(documents, scores)
        ]
        ranks = sorted(ranks, key=lambda x: x.score, reverse=True)
        return ranks[:top_k] if top_k else ranks
