from app.api.v1.routers import api_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", include_in_schema=False)
def read_root():
    return {"message": "health check", "status": "ok"}