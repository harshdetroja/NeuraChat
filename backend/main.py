from fastapi import FastAPI

from db_models import (
    create_db_and_tables,
    SessionDep
)

app = FastAPI(
    title="NeuraChat Backend",
    version="0.1.0",
    description="NeuraChat API powered by FastAPI and uv"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}

