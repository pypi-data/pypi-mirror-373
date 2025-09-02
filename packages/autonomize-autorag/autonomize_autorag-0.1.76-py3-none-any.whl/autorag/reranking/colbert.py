"""ColBERT Reranker module implementation"""

# pylint: disable=line-too-long

from typing import Any, Generator, List, Optional

try:
    import torch
    from transformers import AutoModel, AutoTokenizer  # type: ignore[import-untyped]
except ImportError as err:  # pragma: no cover
    raise ImportError(  # pragma: no cover
        "Unable to locate transformers package. "
        'Please install it with `pip install "autonomize-autorag[huggingface]"`.'
    ) from err

from autorag.reranking.base import Reranker
from autorag.types.reranking import ContentWithScore
from autorag.utilities.logger import get_logger

logger = get_logger()


class ColbertReranker(Reranker):
    """
    ColBERT Reranker implementation.

    This class provides an implementation of the Reranker abstract class
    using the ColBERT to rerank the search results

    Example:
    .. code-block:: python

        from autorag.reranking import ColbertReranker

        model = "colbert-ir/colbertv2.0"
        reranker = ColbertReranker(
            model=model
        )

        query = "token-level interaction in retrieval"
        documents = [
            "ColBERT is a retrieval model that uses token-level interaction.",
            "Transformers like BERT can be used for ranking search results.",
            "This document is about machine learning and natural language processing."
        ]
        top_k = 2

        reranker.rerank(query, documents, top_k)
    """

    def __init__(
        self,
        model_name: str = "colbert-ir/colbertv2.0",
        device: str | None = None,
    ):
        """
        Initializes the SentenceTransformer CrossEncoder model.

        Args:
            model_name (str, optional): Name of the ColBERT-like models. Defaults to "colbert-ir/colbertv2.0".
        """
        super().__init__()
        self._model = AutoModel.from_pretrained(model_name)
        self.device = device or "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Using PyTorch device: %s", device)

        self._model.to(self.device)

        # Not setting clean_up_tokenization_spaces throws a deprecation warning in v4.45.
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_name, clean_up_tokenization_spaces=True
        )

    def _encode_query(self, query: str, **kwargs) -> torch.Tensor:
        """
        Encodes the query into a tensor representation using the ColBERT model.

        Args:
            query (str): The input query string to encode.
            **kwargs: Additional arguments to pass to the tokenizer.

        Returns:
            torch.Tensor: Encoded query tensor.
        """
        query_encoding = self._tokenizer(query, return_tensors="pt", **kwargs).to(
            self.device
        )
        query_embedding = self._model(**query_encoding).last_hidden_state

        return query_embedding

    def _encode_documents(
        self, documents: List[str], **kwargs
    ) -> Generator[torch.Tensor, None, None]:
        """
        Encodes a list of documents into tensor representations using the ColBERT model.

        Args:
            documents (List[str]): List of document strings to encode.
            **kwargs: Additional arguments to pass to the tokenizer.

        Yields:
            Generator[torch.Tensor, None, None]: A generator that yields encoded document tensors.
        """
        for document in documents:
            document_encoding = self._tokenizer(
                document,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
                **kwargs,
            ).to(self.device)
            document_embedding = self._model(**document_encoding).last_hidden_state
            yield document_embedding

    def _calculate_score(self, query: str, documents: List[str]) -> List[float]:
        """
        Calculates similarity scores between the query and each document using cosine similarity.

        Args:
            query (str): The input query string.
            documents (List[str]): List of document strings to compare with the query.

        Returns:
            List[float]: List of similarity scores for each document.
        """
        scores = []
        query_embedding = self._encode_query(query)

        for document_embedding in self._encode_documents(documents):
            sim_matrix = (
                torch.nn.functional.cosine_similarity(  # pylint: disable=not-callable
                    query_embedding.unsqueeze(2),
                    document_embedding.unsqueeze(1),
                    dim=-1,
                )
            )

            max_sim_scores, _ = torch.max(sim_matrix, dim=2)
            scores.append(torch.mean(max_sim_scores, dim=1).item())
        return scores

    def _rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Reranks the search results (documents) based on the search query and the loaded model from
        ColBERT

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting
            them based on score._description_

        Returns:
            List[ContentWithScore]: top_k documents ranked with decreasing reranking score.
        """
        scores = self._calculate_score(query=query, documents=documents)
        ranks = [
            ContentWithScore(content=document, score=score)
            for document, score in zip(documents, scores)
        ]
        ranks = sorted(ranks, key=lambda x: x.score, reverse=True)
        return ranks[:top_k] if top_k else ranks
