from abc import ABC, abstractmethod

class AbstractRole(ABC):
    
    @abstractmethod
    async def assign_role(self, user_id: str, role_id: str, resource_id: str, **kwargs) -> dict:
        """
        Assign a role to a user for a given resource.
        """
        pass

    @abstractmethod
    async def delete_role(self, user_id: str, role_id: str, resource_id: str, **kwargs) -> dict:
        """
        Delete a role from a user for a given resource.
        """
        pass

    @abstractmethod
    async def fetch_all_roles(self, **kwargs) -> dict:
        """
        Fetch all roles.
        """
        pass

    @abstractmethod
    async def fetch_user_roles(self, user_id: str, **kwargs) -> dict:
        """
        Fetch roles assigned to a user.
        """
        pass

    @abstractmethod
    async def fetch_resource_roles(self, resource_id: str, **kwargs) -> dict:
        """
        Fetch roles assigned to a resource.
        """
        pass
