import asyncio
import json

from app.core.startup import verify_rabbitmq_connectivity
from app.messaging.rabbitmq import OTP_EMAIL_QUEUE, rabbitmq
from app.services.email_service import send_otp_email
from app.utils.logger import logger


async def start_email_worker():
    # logger.info("email worker starting...")
    print("email worker starting...", flush=True)
    await verify_rabbitmq_connectivity()
    logger.info("rabbitq verified")
    print("rabbitmq verified", flush=True)
    await rabbitmq.connect()
    logger.info("RabbitMQ connected")
    print("rabbitmq connected", flush=True)
    queue = await rabbitmq.get_queue(OTP_EMAIL_QUEUE)
    logger.info("Queue connected %s", OTP_EMAIL_QUEUE)
    print("Queue connected", OTP_EMAIL_QUEUE)
    async with queue.iterator() as queue_iter:
        logger.info("Waiting for messages...")
        print("Waiting for messages...")
        async for message in queue_iter:
            logger.info("Received email task for %s", message.body)
            print("Received email task for:", message.body)
            async with message.process():
                data = json.loads(message.body.decode())

                email = data["email"]
                otp = data["otp"]

                await send_otp_email(to_email=email, otp_code=otp)


if __name__ == "__main__":
    asyncio.run(start_email_worker())
