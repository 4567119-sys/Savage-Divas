from fastapi import APIRouter

from app.api.v1 import (
    adviser,
    ai_ingest,
    cases,
    clients,
    documents,
    notifications,
)

api_router = APIRouter()

api_router.include_router(clients.router)
api_router.include_router(cases.router)
api_router.include_router(documents.router)
api_router.include_router(ai_ingest.router)
api_router.include_router(adviser.router)
api_router.include_router(notifications.router)