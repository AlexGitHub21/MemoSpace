from fastapi import Depends, HTTPException
from apps.auth.managers import UserManager
from apps.auth.handlers import AuthHandler
from apps.auth.schemas import RegisterUser, UserReturnData, CreateUser
from itsdangerous import URLSafeTimedSerializer, BadSignature
from apps.core.settings import settings
from apps.auth.tasks import send_confirmation_email


class UserService:
    def __init__(self, manager: UserManager = Depends(UserManager), handler: AuthHandler = Depends(AuthHandler)) -> None:
        self.manager = manager
        self.handler = handler
        self.serializer = URLSafeTimedSerializer(secret_key=settings.secret_key.get_secret_value())

    async def register_user(self, user: RegisterUser) -> UserReturnData:
        hashed_password = await self.handler.get_password_hash(user.password)
        new_user = CreateUser(email=user.email, hashed_password=hashed_password)

        user_data = await self.manager.create_user(new_user)
        confirmation_token = self.serializer.dumps(user_data.email)
        send_confirmation_email.delay(to_email=user.email, token=confirmation_token)

        return user_data

    async def confirm_user(self, token: str) -> None:
        try:
            email = self.serializer.loads(token, max_age=3600)
        except BadSignature:
            raise HTTPException(
                status_code=400, detail="Неверный или просроченный токен"
            )
        await self.manager.confirm_user(email=email)