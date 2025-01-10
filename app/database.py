import logging

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import MONGO_DB_NAME, MONGO_URI

logger = logging.getLogger(__name__)

MONGO_CLIENT: AsyncIOMotorClient = None
DATABASE: AsyncIOMotorDatabase = None


def get_db() -> AsyncIOMotorDatabase:
    """Return the initialized async database connection"""
    if DATABASE is None:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    return DATABASE


async def init_db() -> None:
    global MONGO_CLIENT
    try:
        MONGO_CLIENT = AsyncIOMotorClient(MONGO_URI)
        DATABASE = MONGO_CLIENT[MONGO_DB_NAME]
        await DATABASE.command("ping")
        logger.info("Database connection initialized successfully.")
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}.",
        )
