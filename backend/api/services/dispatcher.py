import json

from backend.api.services.publisher import RabbitPublisher
from backend.api.core.config import settings


def routing_service(ch, method, properties, body):
    message = json.loads(body)
    print(f"[Dispatcher] Recebido: {message}")

    target_queue = f"rpa-queue-{message['type']}"

    print(f"[Dispatcher] Target Queue: {target_queue}")

    if target_queue in settings.SPECIALIZED_QUEUES:
        publisher = RabbitPublisher(target_queue)
        publisher.publish(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print("[Dispatcher] Tipo desconhecido, descartando.")

    ch.basic_ack(delivery_tag=method.delivery_tag)
