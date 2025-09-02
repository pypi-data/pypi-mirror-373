import os

from loguru import logger

BIZYDRAFT_DOMAIN = os.getenv("BIZYDRAFT_DOMAIN", "https://api.bizyair.cn")
BIZYDRAFT_SERVER = f"{BIZYDRAFT_DOMAIN}/x/v1"

logger.info(f"{BIZYDRAFT_DOMAIN=} {BIZYDRAFT_SERVER=}")

BIZYAIR_API_KEY = os.getenv("BIZYAIR_API_KEY")
logger.info(f"{BIZYAIR_API_KEY=}")
