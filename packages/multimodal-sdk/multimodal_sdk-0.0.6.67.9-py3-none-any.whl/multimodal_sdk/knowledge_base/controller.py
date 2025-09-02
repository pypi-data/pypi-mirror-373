import aiohttp
import os
import logging
from multimodal_sdk.common.refresh import token_refresh_handler
from multimodal_sdk.common.http_status_handler import HTTPStatusHandler
from multimodal_sdk.common.decorators import log_and_authorize
from multimodal_sdk.common.retry_decorator import retry_on_client_error
from multimodal_sdk.knowledge_base.poll_task_status import PollTaskStatusNamespace
from multimodal_sdk.common.rate_limiter import rate_limiter
from datetime import datetime, timezone, timedelta

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
async def create_collection_func(
    kb_resource_id,
    collection_name,
    ingestion_strategy,
    distance_method=None,
    main_lang=None,
    chunk_strategy=None,
    embedding_strategy=None,
    **kwargs
):
    payload = {
        "name": collection_name,
        "ingestion_strategy": {
            "for_types": ingestion_strategy
        },
        "distance_method": distance_method if distance_method else "cosine",
        "main_lang": main_lang if main_lang else "ja",
        "chunk_strategy": chunk_strategy if chunk_strategy else {"active": True, "max_size": "auto"}
    }

    if embedding_strategy is not None:
        payload["embedding_strategy"] = embedding_strategy
    
    logger.info("KnowledgeBase: create_collection payload: %s", payload)
    
    url = f"{kwargs['base_url']}/knowledge-bases/{kb_resource_id}/collections"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.post(url, json=payload, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_collection_func(
    kb_resource_id,
    collection_name,
    **kwargs
):
    url = f"{kwargs['base_url']}/knowledge-bases/{kb_resource_id}/collections"
    payload = {
        "name": collection_name
    }

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, json=payload, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def get_collection_func(
    kb_resource_id,
    **kwargs
):
    url = f"{kwargs['base_url']}/knowledge-bases/{kb_resource_id}/collections"

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'])

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(201)
async def ingest_data_func(
    kb_resource_id,
    tenant_resource_id,
    namespace,
    batch,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases/{kb_resource_id}"
    logger.info(f"Endpoint URL: {url}")

    form_data = aiohttp.FormData()
    form_data.add_field('namespace', namespace)
    files_to_close = []

    timeout = aiohttp.ClientTimeout(total=600) # 10 minutes

    try:
        for data in batch:
            logger.info(f"Data: {data}")
            # namespace = data.get("namespace")
            # category = data.get("category")
            text = data.get("text")
            file = data.get("data")
            id = data.get("id")
            author = data.get("author", None)
            # Creation date of the data in ISO8601 format.
            created_at = data.get("created_at", None)
            category = data.get("category", [])

            if not author or not created_at:
                raise ValueError("Author and created_at are required fields.")
            
            # Japan TimeZone
            iso_created_at = datetime.fromtimestamp(float(data.get("created_at", 0)), timezone.utc).astimezone(timezone(timedelta(hours=9))).isoformat() if data.get("created_at") else None

            form_data.add_field('record_id', id)
            form_data.add_field('local_str', "ja_JP")
            form_data.add_field('authors', author)
            form_data.add_field('created_at', iso_created_at)
            form_data.add_field('tags', category)

            if text is not None:
                form_data.add_field('text', text)
            
            logger.info("Form data created successfully, till text!")
            
            try:
                if file and os.path.isfile(file):
                    file_path = file  # Keep the original file path
                    file = open(file, 'rb')
                    form_data.add_field('data', file, filename=os.path.basename(file_path))  # Use file_path here
                    files_to_close.append(file)
                elif file:
                    error_message = f"File not found or not a valid file: {file}"
                    logger.error(error_message)
                    raise ValueError(error_message)
            except Exception as e:
                logger.error(f"Error occurred while adding file to form data: {e}")
                raise e

        logger.info("Form data created successfully")

        # Iterate over form data and log
        for key, value in form_data.items():
            logger.info(f"Form data field: {key} = {value}")

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with rate_limiter:
                return await session.post(url, data=form_data, headers=kwargs['headers'], ssl=ssl_context)
    finally:
        for file in files_to_close:
            file.close()
            logger.info(f"Closed file: {file.name}")

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler([200, 202])
async def retrieve_data_func(
    kb_resource_id,
    tenant_resource_id,
    threshold=0.7,
    limit=5,
    timeout=20,
    sync=False,
    history=[],
    inject="",
    namespace=None,
    thread_id="",
    create_thread=False,
    **kwargs
):
    debug_query = kwargs.get("debug_query", [])
    if not isinstance(debug_query, list):
        raise ValueError("debug_query must be a list of (key, value) tuples.")

    # Convert to dict and strip keys and values
    query_dict = {k.strip(): v.strip() for k, v in debug_query if isinstance(k, str) and isinstance(v, str)}

    query = query_dict.get("query")
    if not query or not query.strip():
        raise ValueError("Query is required and cannot be empty.")

    # Final params
    params = query_dict.copy()

    if namespace is not None:
        params["namespace"] = namespace
    if create_thread:
        params['create_thread'] = create_thread
    if thread_id:
        params['thread_id'] = thread_id

    body = {}
    if history:
        body['msg_history'] = history

    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases/{kb_resource_id}/ask"
    logger.info(f"Endpoint URL: {url}")

    logger.info("Query parameters:")
    for key, value in params.items():
        logger.info(f"{key}: {value}")

    if body:
        logger.info(f"Request body: {body}")

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            res = await session.post(url, headers=kwargs['headers'], params=params, json=body, ssl=ssl_context)
            if res.status != 401:
                result = await PollTaskStatusNamespace.poll_task_status_handler(
                    res,
                    status_url=f"https://192.168.20.20/api/v1/tasks/status",
                    task_id_key='task_token',
                    **kwargs
                )
                return result
            return res

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler([200, 202])
async def retrieve_data_func_beta(
    kb_resource_id,
    query,
    namespace=None,
    inject="",
    thread_id="",
    create_thread=False,
    history=[],
    **kwargs
):
    if not query or not query.strip():
        raise ValueError("Query is required and cannot be empty.")

    params = {
        "query": query,
        "inject": inject,
        "version": "beta",
        "namespace": namespace
    }

    body = {}
    # body["query"] = query
    if history:
        body['msg_history'] = history

    if create_thread:
        params['create_thread'] = create_thread
    if thread_id:
        params['thread_id'] = thread_id

    url = f"{kwargs['base_url']}/knowledge-bases/{kb_resource_id}/rag"
    logger.info(f"Endpoint URL: {url}")

    logger.info("Query parameters:")
    for key, value in params.items():
        logger.info(f"{key}: {value}")
    
    if body:
        logger.info(f"Request body: {body}")

    # async with aiohttp.ClientSession() as session:
    #     res = await session.post(url, headers=kwargs['headers'], params=params)
    #     return res
    
    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            res = await session.post(url, headers=kwargs['headers'], params=params)
            if res.status != 401:
                result = await PollTaskStatusNamespace.poll_task_status_handler(
                    res,
                    status_url=f"http://192.168.1.27:5002/api/v1/tasks/status",
                    task_id_key='task_token',
                    **kwargs
                )
                return result
            return res

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler([200, 202])
async def search_data_func(
    tenant_resource_id,
    kb_resource_id,
    namespace,
    query,
    includes=[],
    limit=50,
    offset=0,
    tags=[],
    authors=[],
    creation_from=None,
    creation_to=None,
    **kwargs
):
    if not query or not query.strip():
        raise ValueError("Query is required and cannot be empty.")

    # params = {
    #     "query": query,
    #     "threshold": 0.7,
    #     "limit": 5,
    #     "includes": "distances",
    #     "sync": "true",
    # }

    params=[]
    params.append(('namespace', namespace))
    params.append(('query', query))
    params.append(('limit', limit))
    params.append(('offset', offset))
    if creation_from:
        params.append(('creation_from', creation_from))
    if creation_to:
        params.append(('creation_to', creation_to))
    params.extend([('include', include) for include in includes])
    params.extend([('tag', tag) for tag in tags])
    params.extend([('author', author) for author in authors])

    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases/{kb_resource_id}/search"
    logger.info(f"Endpoint URL: {url}")

    for param in params:
        logger.info(f"Query parameter: {param}")

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            res = await session.get(url, headers=kwargs['headers'], params=params, ssl=ssl_context)
            return res

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(204)
async def delete_item_func(
    tenant_id,
    kb_resource_id,
    record_ids=[],
    namespace=None,
    **kwargs
):
    if not record_ids:
        raise ValueError("Record IDs are required and cannot be empty.")
    
    url = f"{kwargs['base_url']}/stores/{tenant_id}/knowledge-bases/{kb_resource_id}"
    logger.info(f"Endpoint URL: {url}")
    params = [("record_id", rec_id) for rec_id in record_ids]
    params.append(('namespace', namespace))

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.delete(url, headers=kwargs['headers'], params=params, ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def get_ingested_chunks_func(
    kb_resource_id,
    record_id,
    **kwargs
):
    updated_record_id = f"{record_id}"
    # if ingestion_type == "pdf":
    #     if get_chunk_type is None:
    #         updated_record_id = f"{record_id}_script"
    #     else:
    #         updated_record_id = f"{record_id}_summary"
    params = {
        "record_id": updated_record_id,
        "includes": "documents",
        "limit": 5
    }
    url = f"{kwargs['base_url']}/knowledge-bases/{kb_resource_id}/get"

    logger.info(f"Params: {params}")

    # async with aiohttp.ClientSession() as session:
    #     async with rate_limiter:
    #         return await session.get(url, headers=kwargs['headers'], params=params)
    
    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            res = await session.get(url, headers=kwargs['headers'], params=params)
            if res.status != 401:
                result = await PollTaskStatusNamespace.poll_task_status_handler(
                    res,
                    status_url=f"http://192.168.1.27:5002/api/v1/tasks/status",
                    task_id_key='task_token',
                    **kwargs
                )
                return result
            return res

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler([200, 202])
async def get_kb_records_func(
    tenant_id,
    kb_resource_id,
    record_ids=[],
    namespace=None,
    includes=[],
    status=[],
    limit=50,
    tags=[],
    authors=[],
    offset=0,
    creation_from=None,
    creation_to=None,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_id}/knowledge-bases/{kb_resource_id}"
    
    # Correctly format the query parameters with multiple `ids[]`
    params = [('record_id', record_id) for record_id in record_ids]
    params.append(('namespace', namespace))
    params.extend([('include', include) for include in includes])
    params.extend([('status', stat) for stat in status])
    params.append(('limit', limit))
    params.extend([('tag', tag) for tag in tags])
    params.extend([('author', author) for author in authors])
    params.append(('offset', offset))
    if creation_from:
        params.append(('creation_from', creation_from))
    if creation_to:
        params.append(('creation_to', creation_to))

    for param in params:
        logger.info(f"Query parameter: {param}")

    # async with aiohttp.ClientSession() as session:
    #     async with rate_limiter:
    #         res = await session.get(url, headers=kwargs['headers'], params=params, ssl=ssl_context)
    #         if res.status != 401:
    #             result = await PollTaskStatusNamespace.poll_task_status_handler(
    #                 res,
    #                 status_url="https://192.168.20.20/api/v1/tasks/status",
    #                 task_id_key='task_token',
    #                 **kwargs
    #             )
    #             return result
    #         return res

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'], params=params, ssl=ssl_context)


@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def get_namespace_metadata_func(
    tenant_resource_id,
    kb_resource_id,
    namespace,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases/{kb_resource_id}/namespaces/{namespace}"

    # Params: include=authors&include=tags
    params = [
        ("include", "authors"),
        ("include", "tags"),
    ]

    logger.info(f"Params: {params}")
    logger.info(f"URL: {url}")

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.get(url, headers=kwargs['headers'], params=params, ssl=ssl_context)

@retry_on_client_error()
@token_refresh_handler
@log_and_authorize
@HTTPStatusHandler(200)
async def update_ingested_record_func(
    tenant_resource_id,
    kb_resource_id,
    namespace,
    record_id=None,
    author=None,
    tag=None,
    tag_mode=None,
    **kwargs
):
    url = f"{kwargs['base_url']}/stores/{tenant_resource_id}/knowledge-bases/{kb_resource_id}"

    # Build multipart/form-data (only add keys that have a value)
    form = aiohttp.FormData()
    if namespace is not None:
        form.add_field("namespace", str(namespace))
    if record_id is not None:
        form.add_field("record_id", str(record_id))
    if tag is not None:
        form.add_field("tag", str(tag))
    if tag_mode is not None:  # e.g. "discard" | "replace" | "add"
        form.add_field("tag_mode", str(tag_mode))
    if author is not None:
        form.add_field("author", str(author))

    async with aiohttp.ClientSession() as session:
        async with rate_limiter:
            return await session.patch(url, data=form, headers=kwargs['headers'], ssl=ssl_context)
