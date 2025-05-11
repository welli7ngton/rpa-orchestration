import pika
import threading
import json
import time

from orquestration.settings import settings
from orquestration.worker import create_worker, worker_example


def init_conn():
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
    channel = connection.channel()
    return connection, channel


def queue_declare(channel):
    channel.queue_declare(queue=settings.MAIN_QUEUE)
    channel.queue_declare(queue=settings.CALLBACK_QUEUE)
    for q in settings.SPECIALIZED_QUEUES:
        channel.queue_declare(queue=q)


def routing_service(ch, method, properties, body):
    task = json.loads(body)
    print(f"[Dispatcher] Recebido: {task}")

    target_queue = f"rpa-queue-{task['tipo']}"
    if target_queue in settings.SPECIALIZED_QUEUES:
        ch.basic_publish(exchange='', routing_key=target_queue, body=body)
        print(f"[Dispatcher] Redirecionado para {target_queue}")
    else:
        print("[Dispatcher] Tipo desconhecido, descartando.")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_service(ch, method, properties, body):
    result = json.loads(body)
    print(f"[Callback] Resultado: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def init_consumers(channel):
    def start_consumer(queue, callback):
        def thread_fn():
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
            channel.start_consuming()
        threading.Thread(target=thread_fn, daemon=True).start()

    start_consumer(settings.MAIN_QUEUE, routing_service)
    start_consumer(settings.CALLBACK_QUEUE, callback_service)

    for i, q in enumerate(settings.SPECIALIZED_QUEUES, start=1):
        create_worker(queue_name=q, callback=worker_example, worker_id=f"worker-{i}")


def publish_task(channel):
    for i in range(4):
        tarefa = {
            'id': f'task-{i}',
            'tipo': 1 if i % 2 == 0 else 2,
            'caminho': '/scripts/login.robot',
            'variaveis': {'user': 'admin'}
        }
        channel.basic_publish(exchange='', routing_key=settings.MAIN_QUEUE, body=json.dumps(tarefa))
        print(f"[Main] Publicada: {tarefa}")
        time.sleep(0.5)


def main():
    connection, channel = init_conn()
    queue_declare(channel)
    init_consumers(channel)
    publish_task(channel)

    print("[Sistema] Rodando. Pressione CTRL+C para sair.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...")
        connection.close()


if __name__ == "__main__":
    main()
