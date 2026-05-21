from fastapi import FastAPI
from app.services.news_services import get_top_headlines

app = FastAPI()

@app.get("/")
def read_root():
    data = get_top_headlines(country="us")
    return data