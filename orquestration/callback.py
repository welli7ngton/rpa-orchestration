import json


def callback_service(ch, method, properties, body):
    result = json.loads(body)
    print(f"[Callback] Resultado: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
