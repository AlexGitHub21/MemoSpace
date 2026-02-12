from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class EmailSettings(BaseSettings):
    email_host: str
    email_port: int
    email_username: str
    email_password: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf8", extra="ignore"
    )


class RedisSettings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf8", extra="ignore"
    )

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class DBSettings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_ECHO: bool

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf8", extra="ignore"
    )

    # возвращаем строку подключения к бд
    @property
    def get_db_url(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RabbitSettings(BaseSettings):
    RMUSER: str
    RMPASSWORD: str
    RMHOST: str = "localhost"
    RMPORT: int = 5672

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf8", extra="ignore")



class Settings(BaseSettings):
    # DB_SETTINGS: DBSettings = DBSettings()
    # email_settings: EmailSettings = EmailSettings()
    # redis_settings: RedisSettings = RedisSettings()
    secret_key: SecretStr
    templates_dir: str = "templates"
    frontend_url: str
    access_token_expire: int

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf8",
        extra="ignore"
    )

email_settings = EmailSettings()
redis_settings = RedisSettings()
db_settings = DBSettings()
app_settings = Settings()
rabbit_settings = RabbitSettings()
# settings = Settings()
