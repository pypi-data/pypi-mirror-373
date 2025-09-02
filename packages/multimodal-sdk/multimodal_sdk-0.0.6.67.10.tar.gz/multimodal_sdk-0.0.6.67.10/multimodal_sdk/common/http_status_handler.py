import aiohttp
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPStatusHandler:
    def __init__(self, expected_status):
        if isinstance(expected_status, int):
            self.expected_status = [expected_status]
        elif isinstance(expected_status, list):
            self.expected_status = expected_status
        else:
            raise ValueError("Expected status must be an integer or a list of integers")

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            
            try:
                response_json = await response.json()
            except aiohttp.ContentTypeError:
                response_json = {}
                response_text = await response.text()
                logger.error("Non-JSON response received: %s", response_text)
            
            if response.status in self.expected_status:
                return {"status": "success", "status_code": response.status, "data": response_json}
            else:
                return {"status": "error", "status_code": response.status, "data": response_json}

        return wrapper