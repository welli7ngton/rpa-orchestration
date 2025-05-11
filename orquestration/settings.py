class Settings:
    RABBITMQ_HOST = 'localhost'
    MAIN_QUEUE = 'main-queue'
    CALLBACK_QUEUE = 'callback-queue'
    SPECIALIZED_QUEUES = ['rpa-queue-python', 'rpa-queue-robotframework']


settings = Settings()
