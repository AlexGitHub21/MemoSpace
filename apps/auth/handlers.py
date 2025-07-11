from passlib.context import CryptContext
from apps.core.settings import settings


class AuthHandler:
    secret = settings.secret_key.get_secret_value()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)