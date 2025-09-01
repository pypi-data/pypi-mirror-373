# pylint: disable=missing-class-docstring, missing-module-docstring

from typing import List, Optional

from pydantic import BaseModel, Field


class RerankPayload(BaseModel):
    """
    Pydantic model for the input required for reranking.
    """

    query: str = Field(description="Search query to rerank the documents.")
    documents: List[str] = Field(
        description="List of documents fetched through vector search"
    )
    top_k: Optional[int] = Field(
        default=None, description="Number of top documents to return after reranking."
    )


class ContentWithScore(BaseModel):
    """
    Pydantic model for the document having reranking score calculated using the Reranker.
    """

    content: str = Field(description="The reranked document.")
    score: float = Field(
        description="The score assigned to the document after reranking."
    )
