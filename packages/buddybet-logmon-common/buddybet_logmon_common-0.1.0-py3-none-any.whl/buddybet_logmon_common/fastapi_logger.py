import time
from fastapi import Request, Response, FastAPI
from .logger import get_logger

logger = get_logger("fastapi-logger")


def setup_fastapi_logging(app: FastAPI):
    """
    Agrega middleware de logging JSON a una app FastAPI.
    Loggea requests, respuestas y excepciones.
    """

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        try:
            response: Response = await call_next(request)
            process_time = (time.time() - start_time) * 1000

            logger.info(
                "Request procesada",
                extra={
                    "data": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "process_time_ms": round(process_time, 2),
                        "client": request.client.host if request.client else None,
                    }
                }
            )

            return response

        except Exception:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "Excepción en request",
                exc_info=True,
                extra={
                    "data": {
                        "method": request.method,
                        "path": request.url.path,
                        "process_time_ms": round(process_time, 2),
                        "client": request.client.host if request.client else None,
                    }
                }
            )
            raise
