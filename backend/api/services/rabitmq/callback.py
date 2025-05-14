import json

from datetime import datetime

from backend.api.core.logger import setup_logger

logger = setup_logger()


# TODO: Handle callback
# add retry logix, save logs, send report, send notifications...
def callback_service(ch, method, properties, body):
    result = json.loads(body)
    logger.info("[Callback] Recebido", extra={"body": result})

    start = datetime.fromisoformat(result["start_time"])
    end = datetime.fromisoformat(result["end_time"])
    duration = (end - start).total_seconds()

    logger.info("\n[Callback] Resultado", extra={"result": result})
    logger.info("\n[Callback] Tempo de execução", extra={"duration": duration})
