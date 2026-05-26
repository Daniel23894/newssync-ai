from pydantic import BaseModel
from typing import List, Optional


class LLMArticle(BaseModel):
    title: str
    description: Optional[str] = None
    source: str
    topic: Optional[str] = None


class LLMSummaryRequest(BaseModel):
    articles: List[LLMArticle]


class LLMSummaryResponse(BaseModel):
    summary: str
    sentiment: str
    themes: List[str]
    rationale: str
