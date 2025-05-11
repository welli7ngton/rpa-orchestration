import time
import json
from orquestration.settings import settings


def publish_task(channel):
    for i in range(2):
        tarefa = {
            'id': f'task-{i}',
            'type': 1 if i % 2 == 0 else 2,
            'path': '/scripts/login.robot',
            'variables': {'user': 'admin'}
        }
        channel.basic_publish(exchange='', routing_key=settings.MAIN_QUEUE, body=json.dumps(tarefa))
        print(f"[Main] Publicada: {tarefa}")
        time.sleep(5)


def publish_script_task(channel, task):
    channel.basic_publish(exchange='', routing_key=settings.MAIN_QUEUE, body=json.dumps(task))
    print(f"[Main] Publicada: {task}")
    time.sleep(5)
