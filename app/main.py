import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.core.startup import engine, verify_all_dependencies
from app.messaging.rabbitmq import rabbitmq
from app.utils.logger import logger


# Lifespan is a whole application lifecycle hook used to startup and shutdown logic
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    await verify_all_dependencies()

    await rabbitmq.connect()
    await rabbitmq.setup()
    logger.info("RabbitMQ exchange and queue setup completed")
    yield
    # Shutdown
    await rabbitmq.close()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status": "healthy"
    }

# only verify the all three fastapi instances that we define in docker-compose for load balancing
@app.get("/instance", include_in_schema=False)
async def get_instance():
    return {
        "hostname": os.getenv("HOSTNAME")
    }