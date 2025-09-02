from abc import ABC, abstractmethod

class AbstractUserHandler(ABC):

    @abstractmethod
    async def register(self, username: str, email: str, full_name: str, password: str, **kwargs) -> dict:
        """
        Register a new user with the given credentials and return their details.
        """
        pass

    @abstractmethod
    async def login(self, username: str, password: str, **kwargs) -> dict:
        """
        Log in a user with the given username and password.
        """
        pass

    @abstractmethod
    async def refresh(self, **kwargs) -> dict:
        """
        Refresh the user session or authentication token.
        """
        pass

    @abstractmethod
    async def update_password(self, username: str, current_password: str, new_password: str, **kwargs) -> dict:
        """
        Update the password for the given user.
        """
        pass

    @abstractmethod
    async def delete(self, username: str, password: str, **kwargs) -> bool:
        """
        Delete the user with the given username and password.
        """
        pass

    @abstractmethod
    async def get_protected(self, **kwargs) -> dict:
        """
        Access protected resources for the logged-in user.
        """
        pass

    @abstractmethod
    async def revoke(self, **kwargs) -> dict:
        """
        Revoke the user’s access or authentication token.
        """
        pass
