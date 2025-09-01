# AutoRAG

*Powering seamless retrieval and generation workflows for our internal AI systems*

![Python Version](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![PyPI Version](https://img.shields.io/pypi/v/autonomize-autorag?style=for-the-badge&logo=pypi)
![Code Formatter](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Code Linter](https://img.shields.io/badge/linting-pylint-green.svg?style=for-the-badge)
![Code Checker](https://img.shields.io/badge/mypy-checked-blue?style=for-the-badge)
![Code Coverage](https://img.shields.io/badge/coverage-100%25-a4a523?style=for-the-badge&logo=codecov)

## Overview

AutoRAG is a flexible and scalable solution for building Retrieval-Augmented Generation (RAG) systems.

This SDK provides out-of-the-box functionality for creating and managing retrieval-augmented generation workflows, offering a modular, highly-configurable interface. It supports multiple vector stores and leverages http clients like httpx for handling requests, ensuring seamless integration.

## Features

- **Modular architecture**: The SDK allows you to swap, extend, or customize components like retrieval models, vector stores, and response generation strategies.
- **High scalability**: Built to handle large-scale data retrieval and generation, enabling robust, production-ready applications.
- **Celery for dependency injection**: Efficient background tasks with support for distributed task execution.
- **Multi-flow support**: Easily integrate various vector databases (ex: Qdrant, Azure AI Search) with various language models providers (ex: OpenAI, vLLM, Ollama) using standardized public methods for seamless development.

## Installation

1. Create a virtual environment, we recommend [Miniconda](https://docs.anaconda.com/miniconda/) for environment management:
    ```bash
    conda create -n autorag python=3.12
    conda activate autorag
    ```
2. Install the package:
    ```bash
    pip install autonomize-autorag
    ```

To install with optional dependencies like Qdrant, Huggingface, OpenAI, Modelhub, etc., refer to the [Installation Guide](INSTALL.md).


## Usage

The full set of examples can be found in [examples](examples) directory.

### Sync Usage

```python
import os
from autorag.language_models import OpenAILanguageModel

llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

generation = llm.generate(
    message=[{"role": "user", "content": "What is attention in ML?"}],
    model="gpt-4o"
)
```

### Async Usage

Simply use sync methods with `a` prefix and use `await` for each call. Example: `client.generate(...)` becomes `await client.agenerate(...)` and everything else remains the same.

```python
import os
from autorag.language_models import OpenAILanguageModel

llm = OpenAILanguageModel(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

generation = await llm.agenerate(
    message=[{"role": "user", "content": "What is attention in ML?"}],
    model="gpt-4o"
)
```

## Contribution

To contribute in our AutoRAG SDK, please refer to our [Contribution Guidelines](CONTRIBUTING.md).

## License
Copyright (C) Autonomize AI - All Rights Reserved

The contents of this repository cannot be copied and/or distributed without the explicit permission from Autonomize.ai
