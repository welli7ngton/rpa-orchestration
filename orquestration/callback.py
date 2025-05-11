import json


def callback_service(ch, method, _, body):
    result = json.loads(body)
    print(f"[Callback] Resultado recebido: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
