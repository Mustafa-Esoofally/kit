"""Custom API routes for Kit."""

from agno.os.auth import get_authentication_dependency
from agno.os.settings import AgnoAPISettings
from fastapi import APIRouter, Depends


def create_router(settings: AgnoAPISettings) -> APIRouter:
    router = APIRouter(
        dependencies=[Depends(get_authentication_dependency(settings))],
    )

    @router.get("/health")
    def health():
        return {"status": "ok", "service": "kit"}

    return router
