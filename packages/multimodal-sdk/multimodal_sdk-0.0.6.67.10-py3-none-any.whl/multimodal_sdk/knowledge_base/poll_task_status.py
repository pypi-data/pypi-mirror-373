import logging
import aiohttp
import asyncio

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

from multimodal_sdk.common.rate_limiter import rate_limiter

class PollTaskStatusNamespace:

    @staticmethod
    async def poll_task_status_handler(response, status_url, task_id_key, success_status_code=200, polling_interval=2, max_retries=150, **kwargs):

        logger.info("kwargs: %s", kwargs)
        headers = kwargs.get("headers", {})
        try:
            response_json = await response.json()
            logger.info("Initial response: %s", response_json)
        except aiohttp.ContentTypeError:
            response_text = await response.text()
            logger.error("Non-JSON response received: %s", response_text)
            raise ValueError("Failed to process the response JSON.")

        task_id = response_json.get(task_id_key)
        if not task_id:
            raise ValueError("Response does not contain a valid task_id.")
        
        # status_params = {"ids[]": task_id}
        form_data = {"task_token": task_id}

        async with aiohttp.ClientSession() as session:
            retries = 0
            while retries < max_retries:

                logger.info(f"Polling task status with task_id: {task_id}")

                # Apply rate limiting to each API call
                async with rate_limiter:
                    status_res = await session.get(status_url, headers=headers, data=form_data, ssl=ssl_context)

                logger.info("Status response status code: %s", status_res.status)

                try:
                    status_res_json = await status_res.json()
                    logger.info("Status response: %s", status_res_json)
                except aiohttp.ContentTypeError:
                    status_res_text = await status_res.text()
                    logger.error("Non-JSON response received during polling: %s", status_res_text)
                    raise ValueError("Failed to process the status response JSON.")

                if status_res.status == success_status_code:
                    logger.info("Task completed successfully.")
                    return status_res
                
                if status_res.status == 404:
                    logger.info("Thread not found.")
                    return status_res
                
                if status_res.status == 401:
                    logger.error("Unauthorized access.")
                    return status_res
                
                if status_res.status == 500:
                    logger.error(f"Server error occurred during polling for task_id {task_id}: {status_res.status}")
                    raise RuntimeError(f"Server error (500) encountered for task_id {task_id}.")

                retries += 1
                await asyncio.sleep(polling_interval)

            raise TimeoutError(f"Max retries exceeded: {max_retries} attempts made without success.")
