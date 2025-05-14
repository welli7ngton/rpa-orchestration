import pika
import json
from backend.api.core.config import settings


class RabbitPublisher:
    def __init__(self, queue: str):
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        self.channel = self.conn.channel()
        self.queue = queue

    def publish(self, message: dict):

        body = json.dumps(message).encode("utf-8")
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        self.conn.close()
