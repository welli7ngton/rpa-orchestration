import json
from orquestration.settings import settings


def routing_service(ch, method, properties, body):
    task = json.loads(body)
    print(f"[Dispatcher] Recebido: {task}")

    target_queue = f"rpa-queue-{task['type']}"
    print('\n', target_queue, '\n')
    if target_queue in settings.SPECIALIZED_QUEUES:
        ch.basic_publish(exchange='', routing_key=target_queue, body=body)
        print(f"[Dispatcher] Redirecionado para {target_queue}")
    else:
        print("[Dispatcher] Tipo desconhecido, descartando.")

    ch.basic_ack(delivery_tag=method.delivery_tag)
