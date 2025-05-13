import threading

from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.api.services.callback import callback_service
from backend.api.routes.publisher import router
from backend.api.services.dispatcher import routing_service
from backend.api.workers.workers import RPAWorker, SafeWorker
from backend.api.core.config import settings


def start_consumers():
    # Dispatcher
    dispatcher_worker = SafeWorker(settings.MAIN_QUEUE, routing_service, max_workers=1)
    threading.Thread(target=dispatcher_worker.start, daemon=True).start()
    # Callback
    callback_worker = SafeWorker(settings.CALLBACK_QUEUE, callback_service, max_workers=1)
    threading.Thread(target=callback_worker.start, daemon=True).start()

    # RPA Workers
    for queue in settings.SPECIALIZED_QUEUES:
        threading.Thread(target=RPAWorker(queue).start, daemon=True).start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Iniciando projeto...")
    start_consumers()

    yield

    print("[Shutdown] Encerrando projeto...")


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
