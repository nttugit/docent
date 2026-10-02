"""FastAPI entrypoint. Routes stay thin; logic lives in domain modules."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from docent import __version__
from docent.config import get_settings


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    env: str


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Docent", version=__version__)

    @app.get("/health", tags=["ops"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__, env=settings.app_env)

    return app


app = create_app()
