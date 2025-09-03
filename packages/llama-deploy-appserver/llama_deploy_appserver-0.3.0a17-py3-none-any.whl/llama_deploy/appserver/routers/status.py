from fastapi import APIRouter
from llama_deploy.appserver.types import Status, StatusEnum

health_router = APIRouter(
    prefix="/health",
)


@health_router.get("")
async def health() -> Status:
    return Status(
        status=StatusEnum.HEALTHY,
    )
