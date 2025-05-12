from backend.api.core.config import settings
from backend.api.routes.publisher import router
from backend.api.services.dispatcher import routing_service
from backend.api.services.callback import callback_service
from backend.api.workers.base import BaseWorker
from backend.api.workers.runner import script_runner
from fastapi import FastAPI

from contextlib import asynccontextmanager


# FIXME: o contexto das filas de execução está errado, é preciso direcionar corretamente o body das mensagens para
# os workers correspondentes
def start_consumers():
    # Dispatcher
    BaseWorker(settings.MAIN_QUEUE, routing_service, "dispatcher").start()
    # Callback
    BaseWorker(settings.CALLBACK_QUEUE, callback_service, "callback").start()
    # Workers especializados
    for q in settings.SPECIALIZED_QUEUES:
        BaseWorker(q, script_runner, f"worker-{q}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Iniciando projeto...")
    start_consumers()

    yield

    print("[Shutdown] Encerrando projeto...")


app = FastAPI(lifespan=lifespan)
app.include_router(router)
