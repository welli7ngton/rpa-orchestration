from fastapi import APIRouter, Request

from backend.api.core.config import settings
from backend.api.services.rabitmq.publisher import RabbitPublisher

router = APIRouter(prefix='/logs')


@router.post("/post")
async def receive_log(request: Request):
    publisher = RabbitPublisher(settings.LOGS_QUEUE)

    data = await request.json()

    publisher.publish(data)
    return {"status": "log enviado"}
