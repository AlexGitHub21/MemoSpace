from typing import Annotated
from fastapi import Depends, HTTPException, status
from apps.auth.utils import get_token_from_cookie
from apps.auth.handlers import AuthHandler
from apps.auth.managers import UserManager
from apps.auth.schemas import UserVerifySchema


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_cookie)],
    handler: AuthHandler = Depends(AuthHandler),
    manager: UserManager = Depends(UserManager)
) -> UserVerifySchema:
    decode_token = await handler.decode_access_token(token=token)
    user_id = decode_token.get("user_id")
    session_id = decode_token.get("session_id")

    if not await manager.get_access_token(user_id=user_id, session_id=session_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не действителен")

    user = await manager.get_user_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    user.session_id = session_id
    return user