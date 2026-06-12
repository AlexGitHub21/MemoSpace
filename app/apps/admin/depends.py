from app.apps.auth.managers import UserManager
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.apps.auth.utils import get_token_from_cookie
from app.apps.auth.handlers import AuthHandler
from app.apps.admin.managers import AdminManager
from app.apps.admin.schemas import AdminVerifySchema


async def get_current_admin(
    token: Annotated[str, Depends(get_token_from_cookie)],
        handler: AuthHandler = Depends(AuthHandler),
        manager: AdminManager = Depends(AdminManager),
        user_manager: UserManager = Depends(UserManager)
    ) -> AdminVerifySchema:
        decode_token = await handler.decode_access_token(token=token)
        user_id = decode_token.get("user_id")
        session_id = decode_token.get("session_id")

        if not await user_manager.get_access_token(user_id=user_id, session_id=session_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не действителен")

        user = await manager.get_admin_by_id(user_id=user_id)
        if not user.is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")

        user.session_id = session_id
        return user