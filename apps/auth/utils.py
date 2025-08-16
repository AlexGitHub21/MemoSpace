from starlette.requests import Request
from fastapi import HTTPException, status


async def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("Authorization")
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен отсутствует")
    return token