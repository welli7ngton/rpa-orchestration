import time
import pika
import threading

from orquestration.settings import settings
from orquestration.publisher import publish_script_task
from orquestration.callback import callback_service
from orquestration.dispatcher import routing_service
from orquestration.worker import create_worker, script_runner


def init_conn():
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
    channel = connection.channel()
    return connection, channel


def queue_declare(channel):
    channel.queue_declare(queue=settings.MAIN_QUEUE)
    channel.queue_declare(queue=settings.CALLBACK_QUEUE)
    for q in settings.SPECIALIZED_QUEUES:
        channel.queue_declare(queue=q)


def init_consumers():
    def start_consumer(queue, callback):
        def thread_fn():
            connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=queue)  # Garante que existe
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
            print(f"[Consumer:{queue}] Consumindo...")
            channel.start_consuming()
        threading.Thread(target=thread_fn, daemon=True).start()

    start_consumer(settings.MAIN_QUEUE, routing_service)
    start_consumer(settings.CALLBACK_QUEUE, callback_service)


def run_script():
    pass


def main():
    connection, channel = init_conn()
    init_consumers()
    queue_declare(channel)
    # publish_task(channel)

    tarefa_python = {
        'id': 1,
        'type': 'python',
        'path': '/home/welli7ngton/Projects/poc-orquestrador/automations/python/test.py',
        'variables': {'user': 'admin'}
    }

    tarefa_robot = {
        'id': 1,
        'type': 'robotframework',
        'path': '/home/welli7ngton/Projects/poc-orquestrador/test.robot',
        'variables': {'USER': 'admin'}
    }

    publish_script_task(channel, tarefa_python)
    publish_script_task(channel, tarefa_robot)

    create_worker(settings.SPECIALIZED_QUEUES[0], script_runner, worker_id="worker-1")
    create_worker(settings.SPECIALIZED_QUEUES[1], script_runner, worker_id="worker-2")

    print("[Sistema] Rodando. Pressione CTRL+C para sair.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Sistema] Encerrando...")
        connection.close()


if __name__ == "__main__":
    main()
