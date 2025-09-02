import logging
from multimodal_sdk.user_handler.abstract_class import AbstractUserHandler
from multimodal_sdk.common.base import BaseMultiModalRag
from multimodal_sdk.user_handler.controller import (
    login_func,
    register_func,
    refresh_func,
    update_password_func,
    delete_func
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserHandler(BaseMultiModalRag, AbstractUserHandler):
    def __init__(self, oauth_url=None, base_url=None, authz_url=None):
        """
        Initialize the UserHandler with optional URL parameters.
        """
        super().__init__(base_url=base_url)
        self.oauth_url = oauth_url if oauth_url else self.oauth_url
        self.authz_url = authz_url if authz_url else self.authz_url

    def _inject_urls(func):
        """
        Decorator to inject URL parameters into the method's kwargs.
        """
        async def wrapper(self, *args, **kwargs):
            logger.info(f"_inject_urls wrapper args: {args}, kwargs: {kwargs}")

            # Inject the URLs into kwargs
            kwargs['oauth_url'] = self.oauth_url
            kwargs['base_url'] = self.base_url
            kwargs['authz_url'] = self.authz_url

            # Forward the modified kwargs to the next function
            return await func(self, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def get_access_token(response):
        access_token = response.get("data", {}).get("access_token", "")
        if access_token:
            return access_token
        else:
            raise ValueError("Access Token not found in the response.")
    
    @staticmethod
    def get_refresh_token(response):
        refresh_token = response.get("data", {}).get("refresh_token", "")
        if refresh_token:
            return refresh_token
        else:
            raise ValueError("Refresh Token not found in the response.")

    def _token_injection(refresh_token=True, access_token=True):
        """
        Decorator to ensure access_token and refresh_token are present in kwargs.
        """
        def decorator(func):
            async def wrapper(self, *args, **kwargs):
                logger.info(f"_token_injection wrapper args: {args}, kwargs: {kwargs}")

                # Inject tokens if necessary
                if access_token:
                    token = kwargs.get('access_token')
                    if not token:
                        logger.error("Missing access_token.")
                        raise ValueError("access_token is required.")

                if refresh_token:
                    token = kwargs.get('refresh_token')
                    if not token:
                        logger.error("Missing refresh_token.")
                        raise ValueError("refresh_token is required.")
                
                # Forward args and kwargs to the original function
                return await func(self, *args, **kwargs)
            return wrapper
        return decorator

    @_inject_urls
    async def register(self, username: str, email: str, full_name: str, password: str, **kwargs) -> dict:
        """
        Register a new user with the given credentials and return their details.
        """
        logger.info(f"Registering user '{username}' with email '{email}' and full name '{full_name}'.")
        
        result = await register_func(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            **kwargs
        )
        logger.info(f"Registration result: {result}")
        return result

    @_inject_urls
    async def login(self, username: str, password: str, **kwargs) -> dict:
        """
        Log in a user with the given username and password.
        """
        logger.info(f"Logging in user '{username}'.")
        
        result = await login_func(
            username=username,
            password=password,
            **kwargs
        )
        logger.info(f"Login result: {result}")
        return result

    @_inject_urls
    @_token_injection(access_token=False)
    async def refresh(self, **kwargs) -> dict:
        """
        Refresh the user session or authentication token.
        """
        logger.info("Refreshing user session.")
        
        result = await refresh_func(**kwargs)
        logger.info(f"Refresh result: {result}")
        return result

    @_inject_urls
    @_token_injection(refresh_token=True, access_token=True)
    async def update_password(self, username: str, current_password: str, new_password: str, **kwargs) -> dict:
        """
        Update the password for the given user.
        """
        logger.info(f"Updating password for user '{username}'.")

        result = await update_password_func(
            username=username,
            current_password=current_password,
            new_password=new_password,
            **kwargs
        )

        logger.info(f"Password update result: {result}")
        return result

    @_inject_urls
    @_token_injection(refresh_token=True, access_token=True)
    async def delete(self, username: str, password: str, **kwargs) -> bool:
        """
        Delete the user with the given username and password.
        """
        logger.info(f"Deleting user '{username}'.")
        
        result = await delete_func(
            username=username,
            password=password,
            **kwargs
        )
        logger.info(f"User deletion result: {result}")
        return result

    @_inject_urls
    @_token_injection
    async def get_protected(self, **kwargs) -> dict:
        """
        Access protected resources for the logged-in user.
        """
        logger.info("Accessing protected resources.")
        # TODO: Implement access to protected resources (e.g., fetch user-specific data)
        return {"status": "accessed protected resources"}

    @_inject_urls
    @_token_injection
    async def revoke(self, **kwargs) -> dict:
        """
        Revoke the user's access or authentication token.
        """
        logger.info("Revoking user access.")
        # TODO: Implement token revocation logic (e.g., invalidate tokens, update user status)
        return {"status": "access revoked"}
