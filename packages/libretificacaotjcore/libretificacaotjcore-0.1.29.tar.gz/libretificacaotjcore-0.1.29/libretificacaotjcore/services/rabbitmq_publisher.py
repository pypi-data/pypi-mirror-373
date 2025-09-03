import aio_pika
import json
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractQueue

class RabbitMQPublisher:
    def __init__(
        self,
        host: str,
        queue: str,
        username: str,
        password: str,
        vhost: str = "/",
    ):
        self.host = host
        self.queue = queue
        self.username = username
        self.password = password
        self.vhost = vhost

        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.queue_obj: AbstractQueue | None = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=self.host,
            login=self.username,
            password=self.password,
            virtualhost=self.vhost,
            heartbeat=60,
        )

        
        self.channel = await self.connection.channel()
        # garante que mensagens não são perdidas
        self.queue_obj = await self.channel.declare_queue(
            self.queue, durable=True
        )

    async def publish(self, message: dict):
        if not self.channel:
            raise RuntimeError("❌ Canal RabbitMQ não conectado. Chame connect() antes.")

        body = json.dumps(message).encode("utf-8")
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # torna a msg persistente
            ),
            routing_key=self.queue,
        )
        print(f"✅ Mensagem publicada na fila '{self.queue}': {message}")

    async def close(self):
        if self.connection:
            await self.connection.close()
