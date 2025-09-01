# pylint: disable=missing-module-docstring, duplicate-code

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autorag.vector_stores.azure_ai_search import (  # pragma: no cover
        AzureAISearchVectorStore,
    )
    from autorag.vector_stores.base import VectorStore  # pragma: no cover
    from autorag.vector_stores.mongodb_atlas import (  # pragma: no cover
        MongoDBAtlasVectorStore,
    )
    from autorag.vector_stores.qdrant import QdrantVectorStore  # pragma: no cover
    from autorag.vector_stores.vertex_ai_vector_search import (  # pragma: no cover
        VertexAIVectorSearchVectorStore,
    )

__all__ = [
    "VectorStore",
    "AzureAISearchVectorStore",
    "QdrantVectorStore",
    "MongoDBAtlasVectorStore",
    "VertexAIVectorSearchVectorStore",
]

_module_lookup = {
    "VectorStore": "autorag.vector_stores.base",
    "AzureAISearchVectorStore": "autorag.vector_stores.azure_ai_search",
    "QdrantVectorStore": "autorag.vector_stores.qdrant",
    "MongoDBAtlasVectorStore": "autorag.vector_stores.mongodb_atlas",
    "VertexAIVectorSearchVectorStore": "autorag.vector_stores.vertex_ai_vector_search",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(
        f"module {__name__} has no attribute {name}"
    )  # pragma: no cover
