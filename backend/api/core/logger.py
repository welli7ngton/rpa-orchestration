import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(name: str = "rpa_orchestrator") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(funcName)s %(lineno)d'
    )
    log_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(log_handler)

    # evita duplicação de logs
    logger.propagate = False

    return logger
