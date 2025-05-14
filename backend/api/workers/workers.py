import pika

from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

from backend.api.core.config import settings
# from backend.api.workers.runner import script_runner
from backend.api.utils.runner import script_runner
from backend.api.utils.logger import save_log_in_file


class BaseWorker(ABC):
    def __init__(self, queue_name: str, max_workers: int = 1):
        self.queue_name = queue_name
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._wrapped_callback)
        print(f"[{self.queue_name}] Worker started.")
        self.channel.start_consuming()

    def _wrapped_callback(self, ch, method, properties, body):
        self.executor.submit(self._safe_execute, ch, method, properties, body)

    def _safe_execute(self, ch, method, properties, body):
        try:
            self.process_task(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[{self.queue_name}] Worker ERRO: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    @abstractmethod
    def process_task(self, ch, method, properties, body):
        pass


class RPAWorker(BaseWorker):
    def process_task(self, ch, method, properties, body):
        print(f"[{self.queue_name}] RPA Processing")
        script_runner(body)


class SafeWorker(BaseWorker):
    def __init__(self, queue_name, callback_func, max_workers=3):
        super().__init__(queue_name, max_workers)
        self.callback_func = callback_func

    def process_task(self, ch, method, properties, body):
        print(f"[{self.queue_name}] SafeWorker Processing")
        self.callback_func(ch, method, properties, body)


class LoggerWorker(BaseWorker):
    def __init__(self, queue_name, callback_func, max_workers=3):
        super().__init__(queue_name, max_workers)

    def process_task(self, ch, method, properties, body):
        print(f"[{self.queue_name}] LoggerWorker Processing")
        save_log_in_file(body)
