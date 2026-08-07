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
        self._exchange = None

    async def connect(self):
        if self._connection:
            return
        self._connection = await aio_pika.connect_robust(settings.rabbit_mq_url)
        self._channel = await self._connection.channel()

    async def get_channel(self):
        if self._channel is None:
            raise RuntimeError("RabbitMQ channel is not initialized")

        return self._channel

    async def setup(self):
        self._exchange = await self._channel.declare_exchange(
            OTP_EMAIL_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True
        )
        if self._channel is None:
            raise RuntimeError(
                "Channel not initialized"
            )
        queue = await self._channel.declare_queue(OTP_EMAIL_QUEUE, durable=True)

        await queue.bind(self._exchange, routing_key=OTP_EMAIL_ROUTING_KEY)

    async def get_queue(self, queue_name:str):
        if self._channel is None:
           raise RuntimeError("Channel not initialized")
        return await self._channel.declare_queue(
            queue_name,
            passive=True,
        )

    async def get_exchange(self):

        if self._exchange is None:
            raise RuntimeError("RabbitMQ exchange is not initialized")

        return self._exchange

    async def close(self):
        if self._channel:
            await self._channel.close()

        if self._connection:
            await self._connection.close()

        self._channel = None
        self._connection = None
        self._exchange = None


rabbitmq = RabbitMQConnectionManager()
