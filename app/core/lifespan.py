from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully")
    yield
    logger.info("Application finished")
