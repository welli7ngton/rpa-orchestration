import pika
import json

from concurrent.futures import ThreadPoolExecutor

from backend.api.core.config import settings
from backend.api.workers.runner import script_runner


class RPAWorker:
    def __init__(self, queue_name, max_concurrent_jobs=2):
        self.queue_name = queue_name
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print(f"[{self.queue_name}] Worker started.")
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print(f"[{self.queue_name}] Received task")
        self.executor.submit(self.process_task, ch, method, body)

    def process_task(self, ch, method, body):
        try:
            print(f"[{self.queue_name}] Processing: {body}")
            script_runner(json.loads(body), 100)
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
