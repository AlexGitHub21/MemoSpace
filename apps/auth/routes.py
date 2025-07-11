from fastapi import APIRouter, Depends
from apps.auth.schemas import RegisterUser, UserReturnData
from apps.auth.services import UserService
from starlette import status

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    path="/register",
    response_model=UserReturnData,
    status_code=status.HTTP_200_OK
)
async def registration(user: RegisterUser, service: UserService = Depends(UserService)) -> UserReturnData:
    return await service.register_user(user=user)


@auth_router.get(
    path="/register_confirm",
    status_code=status.HTTP_200_OK
)
async def confirm_registration(token: str, service: UserService = Depends(UserService)) -> dict[str, str]:
    await service.confirm_user(token=token)
    return {"message": "Электронная почта подтверждена"}


