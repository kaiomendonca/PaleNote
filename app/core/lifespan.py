from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully")
    yield
    logger.info("Application finished")
