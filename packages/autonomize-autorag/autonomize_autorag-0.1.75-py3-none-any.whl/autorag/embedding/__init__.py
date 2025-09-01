# pylint: disable=missing-module-docstring

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autorag.embedding.base import Embedding  # pragma: no cover
    from autorag.embedding.google import GoogleEmbedding  # pragma: no cover
    from autorag.embedding.huggingface import HuggingFaceEmbedding  # pragma: no cover
    from autorag.embedding.modelhub import ModelhubEmbedding  # pragma: no cover
    from autorag.embedding.openai import (  # pragma: no cover
        AzureOpenAIEmbedding,
        OpenAIEmbedding,
    )

__all__ = [
    "Embedding",
    "AzureOpenAIEmbedding",
    "GoogleEmbedding",
    "OpenAIEmbedding",
    "HuggingFaceEmbedding",
    "ModelhubEmbedding",
]

_module_lookup = {
    "Embedding": "autorag.embedding.base",
    "AzureOpenAIEmbedding": "autorag.embedding.openai",
    "GoogleEmbedding": "autorag.embedding.google",
    "OpenAIEmbedding": "autorag.embedding.openai",
    "HuggingFaceEmbedding": "autorag.embedding.huggingface",
    "ModelhubEmbedding": "autorag.embedding.modelhub",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(
        f"module {__name__} has no attribute {name}"
    )  # pragma: no cover
