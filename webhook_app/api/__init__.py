from fastapi import APIRouter
from .v1.endpoints.webhook import router as router_webhook

main_router = APIRouter()

main_router.include_router(router_webhook)
