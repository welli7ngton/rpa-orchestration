import threading
import pika

from backend.api.core.config import settings


class BaseWorker(threading.Thread):
    def __init__(self, queue, callback, body, worker_id):
        super().__init__(daemon=True)
        self.queue = queue
        self.callback = callback
        self.worker_id = worker_id
        self.body = body

    def run(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        ch = conn.channel()
        ch.queue_declare(queue=self.queue, durable=True)
        ch.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=False, arguments={
            'body': self.body,
            'worker_id': self.worker_id
        })
        ch.start_consuming()
