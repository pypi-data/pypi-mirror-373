import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUIRED_PARAMS = {
    "oauth_url": "",
    "base_url": "",
    "authz_url": "",
    "access_token": "",
    "refresh_token": "",
}

def log_and_authorize(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # logger.info(f"{'#' * 10} {func_name} called with arguments: {{'args': {args}, 'kwargs': {filtered_kwargs}}} {'#' * 10}")
        
        headers = {"Authorization": f"Bearer {kwargs['access_token']}"}
        kwargs['headers'] = headers
        
        result = await func(*args, **kwargs)
        
        return result
    return wrapper