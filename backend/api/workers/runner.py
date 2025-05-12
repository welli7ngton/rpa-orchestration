import json
import subprocess

from backend.api.core.config import settings
from backend.api.services.publisher import RabbitPublisher

from datetime import datetime, timezone


def script_runner(body, worker_id):
    task = json.loads(body)
    path = task.get("path")
    variables = task.get("variables", {})

    print(f"[{worker_id}] Recebido: {task}")

    start_time = datetime.now(timezone.utc).isoformat()
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
            "stderr": result.stderr,
            "start_time": start_time,
            "end_time": datetime.now(timezone.utc).isoformat(),
        }

        RabbitPublisher(settings.CALLBACK_QUEUE).publish(response)

    except Exception as e:
        response = {
            "id": task["id"],
            "status": "exception",
            "worker": worker_id,
            "error": str(e),
            "start_time": start_time,
            "end_time": datetime.now(timezone.utc).isoformat(),
        }

        RabbitPublisher(settings.CALLBACK_QUEUE).publish(response)
