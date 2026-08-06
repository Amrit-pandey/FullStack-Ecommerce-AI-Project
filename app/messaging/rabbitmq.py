# import json

import aio_pika

from app.core.config import settings

OTP_EMAIL_EXCHANGE = "otp_exchange"
OTP_EMAIL_QUEUE = "send_otp_email_queue"
OTP_EMAIL_ROUTING_KEY = "send_otp_email"


class RabbitMQConnectionManager:

    def __init__(self):
        self._connection = None
        self._channel = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(
            settings.rabbit_mq_url
        )
        self._channel = await self._connection.channel()

    async def get_channel(self):
        if self._channel is None:
            raise RuntimeError(
                "RabbitMQ channel is not initialized"
            )

        return self._channel

    async def close(self):
        if self._channel:
            await self._channel.close()

        if self._connection:
            await self._connection.close()

    async def setup(self):
        exchange = await self._channel.declare_exchange(
            OTP_EMAIL_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )

        queue = await self._channel.declare_queue(
            OTP_EMAIL_QUEUE,
            durable=True
        )

        await queue.bind(
            exchange,
            routing_key=OTP_EMAIL_ROUTING_KEY
        )


rabbitmq = RabbitMQConnectionManager()