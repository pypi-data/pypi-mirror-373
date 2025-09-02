"""Modelhub Embedding module implementation"""

# pylint: disable=line-too-long, duplicate-code, invalid-name

from typing import Any, List, Literal, Optional, Union, override

import httpx
from autonomize.core.credential import ModelhubCredential

from autorag.embedding.base import Embedding
from autorag.utilities.logger import get_logger

logger = get_logger()


class ModelhubEmbedding(Embedding):
    """
    Modelhub Embedding implementation.

    This class provides an implementation of the Embedding abstract class
    using our internal Modelhub SDK's embedding models to generate embeddings.

    Example:
    .. code-block:: python

        from autonomize.core.credential import ModelhubCredential
        from autorag.embedding import ModelhubEmbedding

        model_name = "bge_base"
        credential = ModelhubCredential(client_id="modelhub-client", client_secret="xxx")
        model = ModelhubEmbedding(
            credential=credential
        )

        model.create_embedding("Sample text", model_name=model_name)
    """

    MODEL_URL = (
        "https://clinical-llm.modelhub.sprint.autonomize.dev/v1/model/embedding/predict"
    )

    def __init__(
        self,
        credential: ModelhubCredential,
        model_url: Optional[str] = None,
    ):
        """
        Initialize the ModelhubEmbedding instance.

        Args:
            credential ModelhubCredential: The credential object for authorizing with Modelhub.
            model_url (Optional[str]): The Modelhub URL for the embedding model. Defaults to None.
        """

        # Use the provided modelhub URL if available.
        if model_url is not None:
            self.MODEL_URL = model_url

        self._credential = credential

    def _create_embedding(
        self,
        texts: List[str],
        model_name: Literal[
            "bge_base",
            "bge_large",
        ] = "bge_base",
        **kwargs: Any,
    ) -> List[List[float]]:
        """
        Creates embeddings for the provided text(s) using the Modelhub embedding model.

        Args:
            texts (List[str]): The input list of texts to generate embeddings for.
            model_name (str): Modelhub embedding model name. Defaults to "bge_base".
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input texts.
        """
        token = self._credential.get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {"texts": texts, "model_name": model_name}

        # Setting verify=False, so our client doesn't check for SSL certificate.
        with httpx.Client(verify=False, timeout=None) as client:
            response = client.post(self.MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["prediction"]

    @override
    async def acreate_embedding(
        self,
        texts: Union[str, List[str]],
        model_name: Literal[
            "bge_base",
            "bge_large",
        ] = "bge_base",
        **kwargs: Any,
    ) -> List[List[float]]:
        """
        Asynchronously creates embeddings for the provided text(s) using the Modelhub embedding model.

        Args:
            texts (Union[str, List[str]]): The input text or list of texts to generate embeddings for.
            model_name (str): Modelhub embedding model name. Defaults to "bge_base".
            kwargs (Any): Any additional arguments to be used.

        Returns:
            List[List[float]]: A list of embedding vectors for the input text(s).
        """
        token = await self._credential.aget_token()
        if isinstance(texts, str):
            texts = [texts]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {"texts": texts, "model_name": model_name}

        # Setting verify=False, so our client doesn't check for SSL certificate.
        async with httpx.AsyncClient(verify=False, timeout=None) as client:
            response = await client.post(self.MODEL_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["prediction"]
