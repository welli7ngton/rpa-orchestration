import pika
from concurrent.futures import ThreadPoolExecutor
from backend.api.core.config import settings


class SafeWorker:
    def __init__(self, queue_name, callback_func, max_workers=3):
        self.queue_name = queue_name
        self.callback_func = callback_func
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._wrapped_callback)
        print(f"[{self.queue_name}] SafeWorker started.")
        self.channel.start_consuming()

    def _wrapped_callback(self, ch, method, properties, body):
        self.executor.submit(self._safe_execute, ch, method, properties, body)

    def _safe_execute(self, ch, method, properties, body):
        try:
            self.callback_func(ch, method, properties, body)
        except Exception as e:
            print(f"[{self.queue_name}] ERRO: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)
