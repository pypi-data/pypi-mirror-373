import pika
import json


class RabbitMQConsumer:
    def __init__(
        self,
        host: str,
        queue: str,
        username: str,
        password: str,
        vhost: str ="/",
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

    def start_consuming(self, callback):
        def on_message(ch, method, properties, body):
            mensagem = json.loads(body)
            callback(mensagem)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.close()
            
        if not self.channel:
            raise RuntimeError("❌ Canal RabbitMQ não conectado. Chame connect() antes.")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue, on_message_callback=on_message)
        print(
            f'[*] Aguardando mensagens na fila "{self.queue}". Para sair pressione CTRL+C'
        )
        self.channel.start_consuming()

    def close(self):
        if self.connection:
            self.connection.close()
