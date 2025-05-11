class Settings:
    RABBITMQ_HOST = 'localhost'
    MAIN_QUEUE = 'main-queue'
    CALLBACK_QUEUE = 'callback-queue'
    SPECIALIZED_QUEUES = ['rpa-queue-1', 'rpa-queue-2']


settings = Settings()
