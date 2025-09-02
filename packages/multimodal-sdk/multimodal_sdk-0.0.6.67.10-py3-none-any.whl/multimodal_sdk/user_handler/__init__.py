# __init__.py

import asyncio
from multimodal_sdk.user_handler.main import UserHandler


async def main():
    user_handler = UserHandler()

    register_user = await user_handler.register(
        username="plokiju_test_user_123",
        password="Tokyo@6377300390",
        email="masoom.raj@yeail.com",
        full_name="Masoom Raj"
    )

    login_user = await user_handler.login(
        username="plokiju_test_user_123",
        password="Tokyo@6377300370"
    )

    access_token = UserHandler.get_access_token(login_user)
    refresh_token = UserHandler.get_refresh_token(login_user)

    refresh_user_token = await user_handler.refresh(
        refresh_token=refresh_token
    )

    update_password = await user_handler.update_password(
        username="plokiju_test_user_123",
        current_password="Tokyo@6377300390",
        new_password="Tokyo@6377300370",
        access_token=access_token,
        refresh_token=refresh_token
    )

    delete_user = await user_handler.delete(
        username="plokiju_test_user_123",
        password="Tokyo@6377300370",
        access_token=access_token,
        refresh_token=refresh_token
    )
    
if __name__ == "__main__":
    # asyncio.run(main())
    pass