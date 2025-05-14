from typing import List
from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Settings:
    RABBITMQ_HOST: str = getenv("RABBITMQ_HOST", "localhost")
    API_ENDPOINT: str = getenv("API_ENDPOINT", None)

    MAIN_QUEUE: str = getenv("MAIN_QUEUE", "main-queue")
    CALLBACK_QUEUE: str = getenv("CALLBACK_QUEUE", "callback-queue")
    SPECIALIZED_QUEUES: List[str] = [queue.strip() for queue in getenv("SPECIALIZED_QUEUES").split(',')]
    LOGS_QUEUE: str = getenv("LOGS_QUEUE", "logs-queue")


settings = Settings()
