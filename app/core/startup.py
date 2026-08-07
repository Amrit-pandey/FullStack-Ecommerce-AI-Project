import asyncio

import aio_pika
from redis.exceptions import ConnectionError, TimeoutError
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.redis import redis_client
from app.db.database import engine
from app.utils.logger import logger


async def verify_database_connectivity(max_retries: int = 10, retry_delay: int = 2):
    """
    Wait until PostgreSQL is ready before starting the application.
    """

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("PostgreSQL connection established")
            return

        except OperationalError as e:
             logger.warning(
                "Database connection failed (attempt %s/%s). Retrying in %s seconds...",
                attempt,
                max_retries,
                str(e),
                retry_delay,
            )

             await asyncio.sleep(delay=retry_delay)

    raise RuntimeError("Could not connect to PostgreSQL after multiple retries.")


async def verify_redis_connectivity(max_retries:int = 10, retry_delay:int = 2):
    """
    wait until Redis is ready before starting the application
    """

    for attempt in range(1, max_retries + 1):
        try:
            await redis_client.ping()
            logger.info("Redis connection established")
            return

        except (ConnectionError, TimeoutError) as e:
            logger.warning(
                "Redis connection failed (attempt %s/%s). Retrying in %s seconds...",
                attempt,
                max_retries,
                str(e),
                retry_delay
            )

            await asyncio.sleep(delay=retry_delay)

    raise RuntimeError("Could not connect to Redis server after multiple retries.")


async def verify_rabbitmq_connectivity(max_retries:int = 10, retry_delay:int = 2):
    """
    wait until rabbitmq is ready before starting the application
    """

    for attempt in range(1, max_retries + 1):
        try:
            connection = await aio_pika.connect_robust(settings.rabbit_mq_url)
            await connection.close()
            logger.info("RabbitMQ connection established")
            return
        
        except (aio_pika.exceptions.AMQPException, OSError) as e:
            logger.warning(
                "RabbitMQ not ready "
                "(attempt %s/%s): %s. "
                "Retrying in %s seconds...",
                attempt,
                max_retries,
                str(e),
                retry_delay,
            )

            await asyncio.sleep(retry_delay)

    raise RuntimeError("Could not connect to RabbitMQ after multiple retries.")


async def verify_all_dependencies():
    logger.info("Verifying external dependencies...")
    await verify_database_connectivity()
    await verify_redis_connectivity()
    await verify_rabbitmq_connectivity()
    logger.info("All external dependencies are ready.")