import aiohttp
import logging
from multimodal_sdk.common.refresh import token_refresh_handler
from multimodal_sdk.common.http_status_handler import HTTPStatusHandler
from multimodal_sdk.common.decorators import log_and_authorize
from multimodal_sdk.common.retry_decorator import retry_on_client_error
from multimodal_sdk.common.rate_limiter import rate_limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(201)
async def assign_role_func(
    user_id: str,
    role_id: str,
    resource_id: str,
    **kwargs
):
    url = f"{kwargs['authz_url']}/user"

    if user_id:
        payload = [{
            "user_id_granted": user_id,
            "role_id": role_id,
            "resource_id": resource_id
        }]
    else:
        payload = [{
            "role_id": role_id,
            "resource_id": resource_id
        }]

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_role_func(
    user_id: str,
    role_id: str,
    resource_id: str,
    **kwargs
):
    url = f"{kwargs['authz_url']}/user"
    
    if user_id:
        payload = [{
            "user_id_granted": user_id,
            "role_id": role_id,
            "resource_id": resource_id
        }]
    else:
        payload = [{
            "role_id": role_id,
            "resource_id": resource_id
        }]

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, json=payload, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def fetch_all_roles_func(
    **kwargs
):
    url = f"{kwargs['authz_url']}/roles"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def fetch_user_roles_func(
    **kwargs
):
    url = f"{kwargs['authz_url']}/user"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def fetch_resource_roles_func(
    resource_id,
    **kwargs
):
    url = f"{kwargs['authz_url']}/resources/{resource_id}/roles"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'])