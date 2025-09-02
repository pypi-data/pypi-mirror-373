# pylint: disable=missing-module-docstring, duplicate-code

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autorag.language_models.anthropic import (  # pragma: no cover
        AnthropicLanguageModel,
    )
    from autorag.language_models.base import LanguageModel  # pragma: no cover
    from autorag.language_models.google import GoogleLanguageModel  # pragma: no cover
    from autorag.language_models.modelhub import (  # pragma: no cover
        ModelhubLanguageModel,
    )
    from autorag.language_models.ollama import OllamaLanguageModel  # pragma: no cover
    from autorag.language_models.openai import (  # pragma: no cover
        AzureOpenAILanguageModel,
        OpenAILanguageModel,
        RestApiOpenAILanguageModel,
    )

__all__ = [
    "GoogleLanguageModel",
    "ModelhubLanguageModel",
    "LanguageModel",
    "OllamaLanguageModel",
    "OpenAILanguageModel",
    "AzureOpenAILanguageModel",
    "AnthropicLanguageModel",
    "RestApiOpenAILanguageModel",
]

_module_lookup = {
    "GoogleLanguageModel": "autorag.language_models.google",
    "ModelhubLanguageModel": "autorag.language_models.modelhub",
    "LanguageModel": "autorag.language_models.base",
    "OllamaLanguageModel": "autorag.language_models.ollama",
    "OpenAILanguageModel": "autorag.language_models.openai",
    "AzureOpenAILanguageModel": "autorag.language_models.openai",
    "RestApiOpenAILanguageModel": "autorag.language_models.openai",
    "AnthropicLanguageModel": "autorag.language_models.anthropic",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(
        f"module {__name__} has no attribute {name}"
    )  # pragma: no cover
