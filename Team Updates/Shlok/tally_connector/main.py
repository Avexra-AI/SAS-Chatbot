from fastapi import FastAPI
from app.routers import ingest

app = FastAPI(title="Tally Connector Backend")

app.include_router(ingest.router)


@app.get("/")
def health():
    return {"status": "Backend running"}
