import json

import aio_pika

from app.messaging.rabbitmq import (
    OTP_EMAIL_ROUTING_KEY,
    rabbitmq,
)


async def publish_email_task(
    email: str,
    otp: str
):

    message = {
        "email": email,
        "otp": otp,
    }

    exchange = await rabbitmq.get_exchange()

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode()
        ),
        routing_key=OTP_EMAIL_ROUTING_KEY
    )