from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from app.services.news_services import get_top_headlines
from app.services.llm_service import generate_llm_summary, translate_text
from app.models.llm import (
    LLMSummaryRequest,
    LLMSummaryResponse,
    LLMTranslateRequest,
    LLMTranslateResponse
)

app = FastAPI()

@app.get("/")
def read_root(
    country: str = Query("us", min_length=2, max_length=2),
    category: Optional[str] = Query(None, min_length=3, max_length=20),
    search_mode: Optional[str] = Query(None)
):
    data, error_message, error_status = get_top_headlines(
        country=country,
        category=category,
        search_mode=search_mode
    )

    if error_message:
        raise HTTPException(
            status_code=error_status or 502,
            detail=error_message
        )

    return data


@app.post("/llm/summary", response_model=LLMSummaryResponse)
def llm_summary(payload: LLMSummaryRequest):
    result, error_message, error_status = generate_llm_summary(payload.articles)

    if error_message:
        raise HTTPException(
            status_code=error_status or 502,
            detail=error_message
        )

    return result


@app.post("/llm/translate", response_model=LLMTranslateResponse)
def llm_translate(payload: LLMTranslateRequest):
    result, error_message, error_status = translate_text(
        payload.text,
        payload.target_language
    )

    if error_message:
        raise HTTPException(
            status_code=error_status or 502,
            detail=error_message
        )

    return result