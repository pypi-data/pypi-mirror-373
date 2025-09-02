# pylint: disable=missing-class-docstring, missing-module-docstring

from typing import Any, Dict

from pydantic import BaseModel, Field


class VectorStoreQueryResult(BaseModel):
    """
    Pydantic model for vector store search result
    """

    metadata: Dict[str, Any] = Field(
        description="All metadata fields stored in a collection"
    )
    score: float = Field(description="Search similarity score")
