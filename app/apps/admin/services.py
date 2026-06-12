from app.apps.admin.managers import AdminManager
from fastapi import Depends
from app.apps.auth.schemas import UserReturnData
from app.apps.admin.schemas import UpdateUserStatusSchema

class AdminService:
    def __init__(self, manager: AdminManager = Depends(AdminManager)) -> None:
        self.manager = manager

    async def delete_user(self, user_id: int) -> bool:
        return await self.manager.delete_user_by_id(user_id=user_id)

    async def get_all_users(self) -> list[UserReturnData]:
        return await self.manager.get_users()

    async def get_user_by_id(self, user_id: int) -> UserReturnData:
        return await self.manager.get_user_by_id(user_id=user_id)

    async def update_status_user(self, user_id: int, data: UpdateUserStatusSchema) -> UserReturnData:
        return await self.manager.update_status_user(user_id=user_id, data=data)