import logging
from multimodal_sdk.common.base import BaseMultiModalRag
from multimodal_sdk.role.abstract_class import AbstractRole
from multimodal_sdk.role.controller import (
    assign_role_func,
    delete_role_func,
    fetch_all_roles_func,
    fetch_user_roles_func,
    fetch_resource_roles_func
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class _Role(AbstractRole):
    def __init__(self, tenant=None, knowledge_base=None):
        if tenant is not None:
            self.oauth_url = tenant.oauth_url
            self.base_url = tenant.base_url
            self.authz_url = tenant.authz_url
        
        if knowledge_base is not None:
            self.oauth_url = knowledge_base.oauth_url
            self.base_url = knowledge_base.base_url
            self.authz_url = knowledge_base.authz_url
    
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
    
    @_inject_params
    async def assign_role(self, user_id: str, role_id: str, resource_id: str, **kwargs) -> bool:
        """
        Assign a role to a user for a given resource.
        """
        
        result = await assign_role_func(
            user_id=user_id,
            role_id=role_id,
            resource_id=resource_id,
            **kwargs
        )
        logger.info(f"Result for assign role: {result}")
        return result
    
    @_inject_params
    async def delete_role(self, user_id: str, role_id: str, resource_id: str, **kwargs) -> bool:
        """
        Delete a role from a user for a given resource.
        """
        
        result = await delete_role_func(
            user_id=user_id,
            role_id=role_id,
            resource_id=resource_id,
            **kwargs
        )
        logger.info(f"Result for delete role: {result}")
        return result
    
    @_inject_params
    async def fetch_all_roles(self, **kwargs) -> dict:
        """
        Fetch all roles.
        """
        
        result = await fetch_all_roles_func(**kwargs)
        logger.info(f"Result for fetch all roles: {result}")
        return result
    
    @_inject_params
    async def fetch_user_roles(self, **kwargs) -> dict:
        """
        Fetch roles assigned to a user.
        """
        
        result = await fetch_user_roles_func(
            **kwargs
        )
        logger.info(f"Result for fetch user roles: {result}")
        return result
    
    @_inject_params
    async def fetch_resource_roles(self, resource_id: str, **kwargs) -> dict:
        """
        Fetch roles assigned to a resource.
        """
        
        result = await fetch_resource_roles_func(
            resource_id=resource_id,
            **kwargs
        )
        logger.info(f"Result for fetch resource roles: {result}")
        return result
