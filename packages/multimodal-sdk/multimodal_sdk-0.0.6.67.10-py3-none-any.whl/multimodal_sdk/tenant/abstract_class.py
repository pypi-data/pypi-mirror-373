from abc import ABC, abstractmethod

class AbstractTenantHandler(ABC):

    @abstractmethod
    async def create_tenant(self, tenant_name: str, **kwargs) -> dict:
        """Create a new tenant and return its details."""
        pass

    @abstractmethod
    async def delete_tenant(self, tenant_name: str, **kwargs) -> dict:
        """Delete the specified tenant."""
        pass

    @abstractmethod
    async def get_tenant(self, tenant_name: str, **kwargs) -> dict:
        """Get the details of the specified tenant."""
        pass

    @abstractmethod
    async def create_knowledge_base(self, tenant_resource_id: str, kb_name: str, **kwargs) -> dict:
        """Create a new knowledge base under the specified tenant and return its details."""
        pass

    @abstractmethod
    async def delete_knowledge_base(self, tenant_resource_id: str, kb_name: str, **kwargs) -> bool:
        """Delete the specified knowledge base under the tenant."""
        pass

    @abstractmethod
    async def get_knowledge_base(self, tenant_resource_id: str, **kwargs) -> dict:
        """Retrieve the details of a specific knowledge base."""
        pass
