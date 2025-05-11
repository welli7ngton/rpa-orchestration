import pika
import threading
import time
import json
import subprocess

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
    print(f"[{worker_id}] Recebido: \n{task}")

    for i in range(10):
        time.sleep(2)
        print(f"[{worker_id}] Executando step {i + 1}")

    result = {
        'id': task['id'],
        'status': 'done',
        'worker': worker_id
    }

    ch.basic_publish(exchange='', routing_key=settings.CALLBACK_QUEUE, body=json.dumps(result))
    print(f"[{worker_id}] Resultado enviado para Callback Queue")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def script_runner(ch, method, properties, body, worker_id):
    task = json.loads(body)
    path = task.get("path")
    variables = task.get("variables", {})

    print(f"[{worker_id}] Recebido: {task}")

    try:
        if path.endswith(".py"):
            print(f"[{worker_id}] Executando script Python: {path}")
            result = subprocess.run(
                ["python", path],
                capture_output=True,
                text=True
            )

        elif path.endswith(".robot"):
            print(f"[{worker_id}] Executando script Robot: {path}")
            # Monta os argumentos do Robot com -v
            robot_vars = [f"-v {k}:{v}" for k, v in variables.items()]
            result = subprocess.run(
                ["robot", '-d', './results', *robot_vars, path],
                capture_output=True,
                text=True
            )

        else:
            raise ValueError(f"Extensão de script não suportada: {path}")

        status = "done" if result.returncode == 0 else "error"

        response = {
            "id": task["id"],
            "status": status,
            "worker": worker_id,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        response = {
            "id": task["id"],
            "status": "exception",
            "worker": worker_id,
            "error": str(e)
        }

    ch.basic_publish(
        exchange='',
        routing_key=settings.CALLBACK_QUEUE,
        body=json.dumps(response)
    )
    print(f"[{worker_id}] Resultado enviado para Callback Queue")
    ch.basic_ack(delivery_tag=method.delivery_tag)
