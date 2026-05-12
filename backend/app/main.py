from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "NewsSync API is up and running. We gucci"}