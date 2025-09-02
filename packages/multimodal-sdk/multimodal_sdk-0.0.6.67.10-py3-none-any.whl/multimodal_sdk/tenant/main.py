import logging
import asyncio
from multimodal_sdk.common.base import BaseMultiModalRag
from multimodal_sdk.tenant.abstract_class import AbstractTenantHandler
from multimodal_sdk.tenant.controller import (
    create_tenant_func,
    delete_tenant_func,
    get_tenant_func,
    create_knowledge_base_func,
    delete_knowledge_base_func,
    get_knowledge_base_func
)
from multimodal_sdk.knowledge_base import KnowledgeBase
from multimodal_sdk.user_handler import UserHandler
from multimodal_sdk.role.main import _Role

import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Tenant(BaseMultiModalRag, AbstractTenantHandler, _Role):
    def __init__(self, oauth_url=None, base_url=None, authz_url=None):
        super().__init__(base_url=base_url)
        self.oauth_url = oauth_url if oauth_url else self.oauth_url
        self.authz_url = authz_url if authz_url else self.authz_url

        _Role.__init__(self, tenant=self)

    def _inject_params(func):
        async def wrapper(self, *args, **kwargs):
            access_token = kwargs.get('access_token')
            refresh_token = kwargs.get('refresh_token')
            if not access_token or not refresh_token:
                raise ValueError("access_token and refresh_token are required.")

            kwargs['oauth_url'] = self.oauth_url
            kwargs['base_url'] = self.base_url
            kwargs['authz_url'] = self.authz_url

            return await func(self, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def get_tenant_id(response):
        tenant_id = response.get("data", {}).get("tenant", {}).get("id", "")
        if tenant_id:
            return tenant_id
        else:
            raise ValueError("Tenant ID not found in the response.")

    @_inject_params
    async def create_tenant(self, tenant_name: str, **kwargs):
        logger.info("Calling create_tenant with tenant_name: %s, kwargs: %s", tenant_name, kwargs)
        result = await create_tenant_func(
            tenant_name=tenant_name,
            **kwargs
        )

        logger.info("Tenant: create_tenant response: %s", result)
        return result

    @_inject_params
    async def delete_tenant(self, tenant_name: str, **kwargs):
        result = await delete_tenant_func(
            tenant_name=tenant_name,
            **kwargs
        )

        logger.info("Tenant: delete_tenant response: %s", result)
        return result

    @_inject_params
    async def get_tenant(self, **kwargs):
        result = await get_tenant_func(
            **kwargs
        )

        logger.info("Tenant: get_tenant response: %s", result)
        return result

    @_inject_params
    async def create_knowledge_base(self, tenant_resource_id: str, kb_name: str, **kwargs):
        result = await create_knowledge_base_func(
            tenant_resource_id=tenant_resource_id,
            kb_name=kb_name,
            **kwargs
        )

        logger.info("Tenant: create_knowledge_base response: %s", result)
        return result

    @_inject_params
    async def delete_knowledge_base(self, tenant_resource_id: str, kb_name: str, **kwargs):
        result = await delete_knowledge_base_func(
            tenant_resource_id=tenant_resource_id,
            kb_name=kb_name,
            **kwargs
        )

        logger.info("Tenant: delete_knowledge_base response: %s", result)
        return result

    @_inject_params
    async def get_knowledge_base(self, tenant_resource_id: str, **kwargs):
        result = await get_knowledge_base_func(
            tenant_resource_id=tenant_resource_id,
            **kwargs
        )

        logger.info("Tenant: get_knowledge_base response: %s", result)
        return result

async def main():
    logger.info("Testing Tenant class")
    logger.info("Creating Tenant object")

    t = Tenant()
    kb = KnowledgeBase()

    # Users : toyo_test_user_123, toyo_test_user_321, toyo_test_user_456

    # User Handler
    user_handler = UserHandler()

    login_user = await user_handler.login(
        username="mwtestuser002",
        # username="mwtoyo_2312",
        password="Microwave@2025"
    )
    logger.info("login_user final response (mwtoyo_2312): %s", login_user)

    access_token_123 = UserHandler.get_access_token(login_user)
    refresh_token_123 = UserHandler.get_refresh_token(login_user)

    logger.info("access_token_123: %s", access_token_123)

    
    # Get ingested chunks
    # chunks = await kb.get_ingested_chunks(
    #     kb_resource_id="b01fd396-606e-401f-961c-6649266495da",
    #     record_id="1730793175.408909",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123
    # )

    # Ingest Data
    # response = await kb.ingest_data(
    #     kb_resource_id="microwave-org-exd",
    #     tenant_resource_id="microwave-001",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123,
    #     namespace="team-ai",
    #     category="msg",
    #     batch=[{
    #         "author": "Masoom Raj",
    #         "created_at": 1751414400.0,
    #         "text": "hello",
    #         "id": "abcdef123"
    #     }]
    # )

    # Retrieve data
    # response = await kb.retrieve_data(
    #     kb_resource_id="microwave-org-exd",
    #     tenant_resource_id="microwave-001",
    #     # query=f"{{Document Ids of the thread in sequence top to bottom: [['1739406441.871109', 'F08CZMY0LE9', 'F08CN1ELHFH', 'F08CN1FADL7', 'F08DRBP0E5N', 'F08DRBW5VJL'], ['1739407108.086419'], ['1739407156.974659'], ['1739407334.124849']]}}. Based on this thread, answer this query: Explain",
    #     query="Hi",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123,
    #     thread_id="484ad9012e1b48a7971074c47b71de3d",
    #     create_thread="True",
    #     # namespace="org_exd_div",
    #     # inject=""
    # )
    # logger.info("retrieve_data response: %s", response)

    # # Get tenants
    # response = await t.create_tenant(
    #     tenant_name="test-microwave",
    #     access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MTQzMjgyNSwianRpIjoiNTA1M2EyMGYtNWRlZi00NTk5LWExYWQtNzliYzA2OGY2NjhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImExNmRlNjQ3LTMxYWItNGEwMC05YzVlLWJiMTkxYmMwYjQ4MCIsIm5iZiI6MTc1MTQzMjgyNSwiY3NyZiI6IjNlZGIyYTljLTMzYzctNGUwZC1hMzBmLWQ4NDY5ZGZkY2FmNSIsImV4cCI6MTc1MTQzNjQyNX0.hzDWqbpDcR2tRAEnj0afdxkQxiKOuQWt42gooSuHKbA',
    #     refresh_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MTQzMjgyNSwianRpIjoiZmIzZWFiMjAtOGU2OS00YWYxLTk3YjUtMjljMzU3NzgyMjU1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJhMTZkZTY0Ny0zMWFiLTRhMDAtOWM1ZS1iYjE5MWJjMGI0ODAiLCJuYmYiOjE3NTE0MzI4MjUsImNzcmYiOiI1MTcwNThkYS00MzAwLTRkZDUtYjdmMC1jNjcxMjlhMTUzN2QiLCJleHAiOjE3NTQwMjQ4MjV9.4G09WF-J691q5ZTt2AnzFcRZSbtdWN_phZ1OfPRR0T8'
    # )
    # logger.info("get_tenant response: %s", response)

    # Get records
    # response = await kb.get_record_ids(
    #     tenant_id="microwave-test-001",
    #     kb_resource_id="microwave-digital-test",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123,
    #     # record_ids=["1739265561.046389"],
    #     namespace="new-ingestion-test",
    #     includes=["tags", "summaries", "links"],
    #     # status=["draft"],
    #     # limit=50,
    #     # tags=["raw_text"],
    #     offset=1,
    #     creation_from="2025-08-21T00:00:00Z", # In ISO 8601 format
    #     creation_to="2025-09-30T23:59:59Z"
    # )
    # logger.info("get_record_ids response: %s", response)


    # response = await kb.retrieve_data(
    #     kb_resource_id="0e017ade-d094-4c99-847f-fde1cfd5c6a4",
    #     query="Hi there, I need some help",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123,
    #     rag_version="beta",
    #     thread_id="a12114",
    #     create_thread="true",
    # )
    # logger.info("retrieve_data response: %s", response)

    # Delete item
    # response = await kb.delete_item(
    #     kb_resource_id="4998eae9-ec70-4c3e-834d-4a53bbd10253",
    #     record_ids=['F08C7RXSYBU', '1738908501.440269', '1738897965.559129', '1738896561.813679'],
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123
    # )
    # logger.info("(TEST) delete_item response: %s", response)

    # Search Data
    # response = await kb.search_data(
    #     kb_resource_id="ec790cc2-3972-4d8e-a474-3b0010e83455",
    #     query="What does ingestor role means ?",
    #     access_token=access_token_123,
    #     refresh_token=refresh_token_123
    # )
    # logger.info("(TEST) search_data response: %s", response)


    # TEST RATE LIMIT
    # Define the retrieve_data call parameters
    # params = {
    #     "kb_resource_id": "0e017ade-d094-4c99-847f-fde1cfd5c6a4",
    #     "query": "Hi there, I need some help",
    #     "access_token": access_token_123,
    #     "refresh_token": refresh_token_123,
    #     "rag_version": "beta",
    #     "thread_id": "a12114",
    # }
    
    # # Create a list of tasks for 10 concurrent calls to retrieve_data
    # tasks = [kb.retrieve_data(**params) for _ in range(5)]
    
    # # Log the start of the test
    # logger.info("Starting 10 concurrent requests to test rate limiting")

    # # Run tasks concurrently and gather responses
    # responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # # Log each response
    # for i, response in enumerate(responses):
    #     logger.info("Response %d: %s", i + 1, response)




if __name__ == "__main__":
    asyncio.run(main())
