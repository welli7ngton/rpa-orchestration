import pika
import threading
import time
import json
from typing import Callable

from orquestration.settings import settings


def create_worker(queue_name: str, callback: Callable, **callback_args):
    def worker_thread():
        connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)

        def wrapped_callback(ch, method, properties, body):
            callback(ch, method, properties, body, **callback_args)

        print(f"[{callback_args.get('worker_id')}] Aguardando tarefas em {queue_name}")
        channel.basic_consume(queue=queue_name, on_message_callback=wrapped_callback, auto_ack=False)
        channel.start_consuming()

    threading.Thread(target=worker_thread, daemon=True).start()


def worker_example(ch, method, properties, body, worker_id):
    task = json.loads(body)
    print(f"[{worker_id}] Recebido: {task}")

    for i in range(20):
        time.sleep(5)
        print(f"[{worker_id}] Executando step {i + 1}")

    result = {
        'id': task['id'],
        'status': 'done',
        'worker': worker_id
    }

    ch.basic_publish(exchange='', routing_key=settings.CALLBACK_QUEUE, body=json.dumps(result))
    print(f"[{worker_id}] Resultado enviado para Callback Queue")
    ch.basic_ack(delivery_tag=method.delivery_tag)
