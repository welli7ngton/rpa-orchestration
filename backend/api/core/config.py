from typing import List
from os import getenv
from dotenv import load_dotenv

load_dotenv()


class Settings:
    RABBITMQ_HOST: str = getenv("RABBITMQ_HOST", "localhost")
    MAIN_QUEUE: str = getenv("MAIN_QUEUE", "main-queue")
    CALLBACK_QUEUE: str = getenv("CALLBACK_QUEUE", "callback-queue")
    SPECIALIZED_QUEUES: List[str] = [queue.strip() for queue in getenv('_SPECIALIZED_QUEUES').split(',')]


settings = Settings()
