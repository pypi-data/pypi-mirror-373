from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class SmsSettings(BaseSettings):
    """
        短信配置
        Sms Settings
    """
    CACHE_BACKEND: Optional[str] = Field(default="redis", description="缓存类型", title="cache_backend(redis, inmemory)")
    CACHE_BACKEND_DSN: Optional[str] = Field(default="redis://localhost:6379/1", description="缓存dsn", title="cache_backend_dsn")
    IS_LIMIT_CODE_FREQUENCY: Optional[bool] = Field(default=True, description="是否限制频率", title="code frequency check")
    CHECK_CODE_RESEND_TIME: Optional[int] = Field(default=1, description="验证码重新发送时间", title="check code resend time (minute)")
    DEFAULT_CODE: Optional[int] = Field(default="654123", description="默认验证码", title="sms default code")

    class Config:
        env_prefix = 'Sms_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'



