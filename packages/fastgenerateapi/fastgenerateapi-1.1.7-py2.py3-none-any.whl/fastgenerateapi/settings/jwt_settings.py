from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class JWTSettings(BaseSettings):
    """
    jwt配置
    """
    SECRET_KEY: Optional[str] = Field(..., description="认证密钥", title="JWT SECRET KEY")
    ALGORITHM: Optional[str] = Field(default='HS256', description="认证密钥", title="JWT ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = Field(default=30, description="过期时间 (分钟)", title="JWT Access Token")
    REFRESH_TOKEN_EXPIRE_MINUTES: Optional[int] = Field(default=60, description="过期时间（分钟）", title="JWT Refresh Token")

    class Config:
        env_prefix = 'JWT_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'



