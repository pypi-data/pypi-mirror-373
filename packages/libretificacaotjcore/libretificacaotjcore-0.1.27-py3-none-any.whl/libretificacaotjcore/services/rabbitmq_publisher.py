import pika
import json

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
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            credentials=credentials,
            virtual_host=self.vhost,
            heartbeat=60,
            blocked_connection_timeout=300,
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, message: dict):
        if not self.channel:
            raise RuntimeError("❌ Canal RabbitMQ não conectado. Chame connect() antes.")

        body = json.dumps(message)
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # torna a mensagem persistente
            )
        )
        print(f"✅ Mensagem publicada na fila '{self.queue}': {message}")

    def close(self):
        if self.connection:
            self.connection.close()
