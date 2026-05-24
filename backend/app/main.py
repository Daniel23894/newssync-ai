from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from app.services.news_services import get_top_headlines

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