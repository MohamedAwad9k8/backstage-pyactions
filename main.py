import time
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.discovery import register_modules
from app.core.logging import logger

app = FastAPI(
    title=settings.APP_NAME,
    description="Extend Backstage automation capabilities with Python workflows.",
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = (await request.body()).decode("utf-8", errors="replace")
    logger.info(
        f"Request: {request.method} {request.url.path} | Body: {body[:500]}"
    )
    start = time.time()
    response = await call_next(request)
    logger.info(
        f"Response: {response.status_code} | {time.time() - start:.2f}s"
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


register_modules(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
