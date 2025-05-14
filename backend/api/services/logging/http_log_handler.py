import logging
import httpx
from backend.api.core.config import settings


class HttpLogHandler(logging.Handler):
    def __init__(self, endpoint_url=f"{settings.API_ENDPOINT}/logs/post"):
        super().__init__()
        self.endpoint_url = endpoint_url
        self.formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def emit(self, record):
        try:
            timestamp = self.formatter.formatTime(record)

            data = {
                "level": record.levelname,
                "message": self.format(record),
                "timestamp": timestamp,
                "type": "python"
            }

            with httpx.Client() as client:
                client.post(self.endpoint_url, json=data)

        except Exception as e:
            print(f"[HttpLogHandler] Erro ao enviar log: {e}")
