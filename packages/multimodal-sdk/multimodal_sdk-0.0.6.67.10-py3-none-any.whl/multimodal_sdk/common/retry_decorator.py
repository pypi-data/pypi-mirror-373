from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def custom_retry_condition(exception):
    # Retry for all ClientError exceptions except 401
    return (
        (isinstance(exception, aiohttp.ClientResponseError) and exception.status != 401)
        or isinstance(exception, (aiohttp.ClientConnectionError, aiohttp.ServerDisconnectedError, aiohttp.ClientOSError))
    )

def retry_on_client_error():
    # 2, 4, 8, 16, 20 seconds backoff
    return retry(
        retry=retry_if_exception(custom_retry_condition),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=1, max=20),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
