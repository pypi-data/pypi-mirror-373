# pylint: disable=missing-module-docstring, duplicate-code

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autorag.reranking.base import Reranker  # pragma: no cover
    from autorag.reranking.colbert import ColbertReranker  # pragma: no cover
    from autorag.reranking.cross_encoder import CrossEncoderReranker  # pragma: no cover
    from autorag.reranking.modelhub import ModelhubReranker  # pragma: no cover

__all__ = [
    "Reranker",
    "ColbertReranker",
    "CrossEncoderReranker",
    "ModelhubReranker",
]

_module_lookup = {
    "Reranker": "autorag.reranking.base",
    "ColbertReranker": "autorag.reranking.colbert",
    "CrossEncoderReranker": "autorag.reranking.cross_encoder",
    "ModelhubReranker": "autorag.reranking.modelhub",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(
        f"module {__name__} has no attribute {name}"
    )  # pragma: no cover
