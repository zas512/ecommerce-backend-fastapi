import sys
import os
from loguru import logger
from app.core.config import settings

logger.remove()

if settings.ENV_MODE == "dev":
    logger.add(
        sys.stdout,
        level="DEBUG",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.info("LOGGING MODE: Console (Dev)")

else:
    LOG_DIR = "app/logs"
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger.add(
        os.path.join(LOG_DIR, "app.log"),
        level="INFO",
        rotation="5 MB",
        retention="3 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}",
    )
