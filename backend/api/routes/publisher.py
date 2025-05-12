from fastapi import APIRouter, HTTPException, BackgroundTasks

from backend.api.services.publisher import RabbitPublisher
from backend.api.schemas.schemas import TaskRequest, TaskResponse
from backend.api.core.config import settings

router = APIRouter(prefix="/v1")


@router.post("/tasks", response_model=TaskResponse)
def create_task(req: TaskRequest, background: BackgroundTasks):
    publisher = RabbitPublisher(settings.MAIN_QUEUE)
    message = req.model_dump()
    # publica na fila principal
    publisher.publish(message)
    publisher.close()
    # TODO opcional: iniciar consumidor de callback em background
    # background.add_task(start_callback_consumer)
    return TaskResponse(id=message["id"], status="queued")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_status(task_id: int):
    # TODO
    # consulta em memória, DB ou cache o status
    # status = retrieve_status(task_id)
    # if not status:
    #     raise HTTPException(404, "Task not found")
    # return TaskResponse(id=task_id, status=status)
    return {"error": "Sorry, not implemented yet."}
