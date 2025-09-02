import uvicorn
from fastapi import FastAPI

from superlinked.server.app import ServerApp
from superlinked.server.configuration.settings import settings
from superlinked.server.logger import ServerLoggerConfigurator


def get_app() -> FastAPI:
    return ServerApp().app


def main() -> None:
    ServerLoggerConfigurator.setup_logger()
    uvicorn.run(
        "superlinked.server.__main__:get_app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        workers=settings.WORKER_COUNT,
        log_config=None,
        factory=True,
        loop="asyncio",
    )


if __name__ == "__main__":
    main()
