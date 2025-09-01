import logging

from crypticorn.auth import Verify200Response as Verify200Response
from auth import AuthHandler
from python.crypticorn_utils.types import ApiEnv, BaseUrl

logger = logging.getLogger(__name__)

auth_handler = AuthHandler(base_url=)
logger.info(f"Auth URL: {auth_handler.client.config.host}")
