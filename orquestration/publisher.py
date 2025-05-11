import time
import json
from orquestration.settings import settings


def publish_task(channel):
    for i in range(5):
        tarefa = {'id': f'task-{i}', 'tipo': 1 if i % 2 == 0 else 2}
        channel.basic_publish(exchange='', routing_key=settings.MAIN_QUEUE, body=json.dumps(tarefa))
        print(f"[Main] Tarefa publicada: {tarefa}")
        time.sleep(0.5)
