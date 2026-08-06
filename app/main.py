from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.core.startup import (
    engine,
    verify_database_connectivity,
    verify_redis_connectivity,
)
from app.messaging.rabbitmq import rabbitmq


# Lifespan is a whole application lifecycle hook used to startup and shutdown logic
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    await verify_redis_connectivity()
    await verify_database_connectivity()
    
    await rabbitmq.connect()
    await rabbitmq.setup()
    yield
    # Shutdown
    await rabbitmq.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", include_in_schema=False)
def read_root():
    return {"message": "health check", "status": "ok"}