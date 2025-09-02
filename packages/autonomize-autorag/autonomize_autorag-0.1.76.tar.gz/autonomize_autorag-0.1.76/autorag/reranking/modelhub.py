"""Modelhub Embedding module implementation"""

# pylint: disable=line-too-long, duplicate-code, invalid-name

from typing import Any, List, Literal, Optional, override

import httpx
from autonomize.core.credential import ModelhubCredential

from autorag.reranking.base import Reranker
from autorag.types.reranking import ContentWithScore
from autorag.utilities.logger import get_logger

logger = get_logger()


class ModelhubReranker(Reranker):
    """
    Modelhub Reranking implementation.

    This class provides an implementation of the Reranker abstract class
    using our internal Modelhub SDK's embedding models to rerank search documents.

    Example:
    .. code-block:: python

        from autonomize.core.credential import ModelhubCredential
        from autorag.reranking import ModelhubReranker

        model = "cross_encoder"
        top_k = 2
        query = "token-level interaction in retrieval"
        documents = [
                "CrossEncoder is a retrieval model that uses token-level interaction.",
                "Transformers like BERT can be used for ranking search results.",
                "This document is about machine learning and natural language processing."
            ]
        credential = ModelhubCredential(client_id="modelhub-client", client_secret="xxx")
        reranker = ModelhubReranker(
            credential=credential
        )

        reranker.rerank(query=query, documents=documents, top_k=top_k, model=model)
    """

    MODEL_URL = (
        "https://clinical-llm.modelhub.sprint.autonomize.dev/v1/model/reranking/predict"
    )

    def __init__(self, credential: ModelhubCredential, model_url: Optional[str] = None):
        """
        Initialize the ModelhubReranker instance.

        Args:
            credential ModelhubCredential: The credential object for authorizing with Modelhub
            model_url (Optional[str]): The Modelhub URL for the reranking model. Defaults to None.
        """

        # Use the provided modelhub URL if available.
        if model_url is not None:
            self.MODEL_URL = model_url

        self._credential = credential

    def _rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        model: Literal[
            "cross_encoder",
            "colbert",
        ] = "cross_encoder",
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Reranks the search results (documents) based on the search query and logged model on Modelhub.

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting.
            model (Literal["cross_encoder", "colbert", ], optional): The logged model name on Modelhub.
            Defaults to "cross_encoder".
        Returns:
            List[ContentWithScore]: Reranked top_k documents with reranking score.
        """

        token = self._credential.get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "model": model,
            "input_data": {"query": query, "documents": documents, "top_k": top_k},
        }

        # Setting verify=False, so our client doesn't check for SSL certificate.
        with httpx.Client(verify=False, timeout=None) as client:
            response = client.post(self.MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            predictions = response.json()["prediction"]
            return [ContentWithScore(**prediction) for prediction in predictions]

    @override
    async def arerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        model: Literal[
            "cross_encoder",
            "colbert",
        ] = "cross_encoder",
        **kwargs: Any,
    ) -> List[ContentWithScore]:
        """
        Asynchronously Reranks the search results (documents) based on the search query and logged model on Modelhub.

        Args:
            query (str): Search Query to do vector search.
            documents (List[str]): Documents fetched through vector search operation.
            top_k (int): Number of documents to keep in the results after sorting.
            model (Literal["cross_encoder", "colbert", ], optional): The logged model name on Modelhub.
            Defaults to "cross_encoder".
        Returns:
            List[ContentWithScore]: Reranked top_k documents with reranking score.
        """

        token = await self._credential.aget_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "model": model,
            "input_data": {"query": query, "documents": documents, "top_k": top_k},
        }

        # Setting verify=False, so our client doesn't check for SSL certificate.
        async with httpx.AsyncClient(verify=False, timeout=None) as client:
            response = await client.post(self.MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            predictions = response.json()["prediction"]
            return [ContentWithScore(**prediction) for prediction in predictions]
