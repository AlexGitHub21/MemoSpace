from fastapi import APIRouter, Depends
from app.apps.admin.services import AdminService
from app.apps.admin.schemas import UpdateUserStatusSchema, UserReturnData
from starlette import status
from app.apps.admin.depends import get_current_admin


admin_router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@admin_router.get(
    path="/users",
    response_model=list[UserReturnData],
    status_code=status.HTTP_200_OK)
async def get_all_users(service: AdminService = Depends(AdminService)) -> list[UserReturnData]:
    return await service.get_all_users()


@admin_router.get(
    path="/users/{user_id}",
    response_model=UserReturnData,
    status_code=status.HTTP_200_OK
)
async def get_user_by_id(
        user_id: int,
        service: AdminService = Depends(AdminService)
) -> UserReturnData:
    return await service.get_user_by_id(user_id)


@admin_router.patch(
    path="/users/{user_id}",
    response_model=UserReturnData,
    status_code=status.HTTP_200_OK
)
async def update_is_superuser(
        user_id: int,
        data: UpdateUserStatusSchema,
        service: AdminService = Depends(AdminService)) -> UserReturnData:
    return await service.update_status_user(user_id=user_id, data=data)


@admin_router.delete(
    path="/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def user_delete(user_id: int, service: AdminService = Depends(AdminService)):
    await service.delete_user(user_id)
