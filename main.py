from fastapi import FastAPI
from api.query import router as query_router
from api.ingest import router as ingest_router
# from api.auth import router as auth_router



app = FastAPI(title="Geo-Spatial RAG Real Estate Agent")


app.include_router(query_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")

@app.get("/")
def health():
    return {"status": "running"}
