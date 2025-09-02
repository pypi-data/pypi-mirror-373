from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    URL: Optional[str] = Field(default="redis://127.0.0.1", description="IP地址")
    PORT: Optional[int] = Field(default=6379, description="映射端口")
    PASSWORD: Optional[str] = Field(default="", description="密码")

    class Config:
        env_prefix = 'REDIS_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'
