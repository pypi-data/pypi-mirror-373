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
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(201)
async def create_tenant_func(tenant_name, **kwargs):
    url = f"{kwargs['base_url']}/stores"
    payload = {"name": tenant_name}

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload, headers=kwargs['headers'], ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_tenant_func(tenant_name, **kwargs):
    url = f"{kwargs['base_url']}/stores"
    payload = {"name": tenant_name}

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, json=payload, headers=kwargs['headers'], ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def get_tenant_func(**kwargs):
    url = f"{kwargs['base_url']}/stores"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'], ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(201)
async def create_knowledge_base_func(
    tenant_resource_id,
    kb_name,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases"
    payload = {"name": kb_name}

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload, headers=kwargs['headers'], ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_knowledge_base_func(
    tenant_resource_id,
    kb_name,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases"
    payload = {"name": kb_name}

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, json=payload, headers=kwargs['headers'], ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def get_knowledge_base_func(
    tenant_resource_id,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'], ssl=ssl_context)

