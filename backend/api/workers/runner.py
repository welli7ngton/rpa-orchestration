import json
import subprocess
import pytz

from backend.api.core.config import settings
from backend.api.services.publisher import RabbitPublisher

from datetime import datetime


def script_runner(body: bytes):
    task = json.loads(body.decode('utf-8'))

    path = task.get("path")
    variables = task.get("variables", {})

    print(f"[WORKER] Recebido: {task}")

    start_time = datetime.now(pytz.UTC)
    try:
        if path.endswith(".py"):
            print(f"[WORKER] Executando script Python: {path}")
            result = subprocess.run(
                ["python", path],
                capture_output=True,
                text=True
            )

        elif path.endswith(".robot"):
            print(f"[WORKER] Executando script Robot: {path}")

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
            "task_id": task["task_id"],
            "status": status,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now(pytz.UTC).isoformat(),
        }

        RabbitPublisher(settings.CALLBACK_QUEUE).publish(response)

    except Exception as e:
        response = {
            "task_id": task["task_id"],
            "status": "exception",
            "error": str(e),
            "start_time": start_time.isoformat(),
            "end_time": datetime.now(pytz.UTC).isoformat(),
        }

        RabbitPublisher(settings.CALLBACK_QUEUE).publish(response)
