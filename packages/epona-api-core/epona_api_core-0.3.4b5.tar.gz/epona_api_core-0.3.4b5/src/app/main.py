import logging

import uvicorn
from fastapi import FastAPI

from app.routes import ping
from epona.auth import routers as auth
from epona.layers import routers as layers
from epona.pessoas import routers as pessoas

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI(title="api-core", version="0.3.1")

    application.include_router(auth.router, prefix="/auth", tags=["auth"])
    application.include_router(pessoas.router, prefix="/pessoas", tags=["pessoas"])
    application.include_router(ping.router, prefix="/ping", tags=["ping"])
    application.include_router(layers.router, prefix="/layers", tags=["layers"])

    return application


app = create_application()


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
