import aiohttp
import logging
from multimodal_sdk.common.refresh import token_refresh_handler
from multimodal_sdk.common.http_status_handler import HTTPStatusHandler
from multimodal_sdk.common.decorators import log_and_authorize
from multimodal_sdk.common.retry_decorator import retry_on_client_error
from multimodal_sdk.common.rate_limiter import rate_limiter

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry_on_client_error()
@HTTPStatusHandler(201)
async def login_func(
    username,
    password,
    **kwargs
):
    # log kwargs
    logger.info(f"kwargs: {kwargs}")
    url = f"{kwargs['oauth_url']}/login"
    logger.info(f"URL: {url}")
    payload = {
        "username": username,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload, ssl=ssl_context)

@retry_on_client_error()
@HTTPStatusHandler(201)
async def register_func(
    username,
    email,
    full_name,
    password,
    **kwargs
):
    logger.info(f"kwargs: {kwargs}")
    url = f"{kwargs['oauth_url']}/register"
    logger.info(f"URL: {url}")
    payload = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password
    }

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload)

@retry_on_client_error()
@HTTPStatusHandler(201)
async def refresh_func(
    **kwargs
):
    logger.info(f"kwargs: {kwargs}")
    url = f"{kwargs['oauth_url']}/refresh"
    logger.info(f"URL: {url}")

    headers = {"Authorization": f"Bearer {kwargs['refresh_token']}"}

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, headers=headers)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def update_password_func(
    username,
    current_password,
    new_password,
    **kwargs
):
    logger.info(f"kwargs: {kwargs}")
    url = f"{kwargs['oauth_url']}/login"
    logger.info(f"URL: {url}")

    payload = {
        "username": username,
        "current_password": current_password,
        "new_password": new_password
    }
    
    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.patch(url, json=payload, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_func(
    username,
    password,
    **kwargs
):
    logger.info(f"kwargs: {kwargs}")
    url = f"{kwargs['oauth_url']}/login"
    logger.info(f"URL: {url}")

    payload = {
        "username": username,
        "password": password
    }
    
    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, json=payload, headers=kwargs['headers'])