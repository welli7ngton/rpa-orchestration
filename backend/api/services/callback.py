import json

from datetime import datetime

from backend.api.core.logger import setup_logger


# TODO: Handle callback
# add retry logix, save logs, send report, send notifications...
def callback_service(ch, method, properties, body):
    logger = setup_logger()
    logger.info("[Callback] Recebido", extra={"body": body})
    result = json.loads(body)

    start = datetime.fromisoformat(result["start_time"])
    end = datetime.fromisoformat(result["end_time"])
    duration = (end - start).total_seconds()

    logger.info("[Callback] Resultado", extra={"result": result})
    logger.info("[Callback] Tempo de execução", extra={"duration": duration})

    ch.basic_ack(delivery_tag=method.delivery_tag)
