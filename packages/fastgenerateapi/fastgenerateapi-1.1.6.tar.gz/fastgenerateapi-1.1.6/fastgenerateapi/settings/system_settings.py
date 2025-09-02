from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class SystemSettings(BaseSettings):
    """
        System Settings
    """
    NAME: str = Field(default='fastgenerateapi', description="项目名称")
    HOST: Optional[str] = Field(default='127.0.0.1', description="本地运行host")
    PORT: Optional[int] = Field(default=8001, description="本地运行port")
    DEBUG: bool = Field(default=True, description="是否开启调试模式，本地修改自动重载")

    # BASE_DIR: Union[PathType, str, None]
    DOMAIN: Optional[str] = Field(default="http://127.0.0.1:8001", description="服务域名（对外暴露的域名地址包含协议）")
    FIELD_SECRET: Optional[str] = Field(default=None, description="字段加密密钥")

    # 分布式id
    WORKER_ID: Optional[int] = Field(default='1', description="数据中心（机器区域）ID")
    DATACENTER_ID: Optional[int] = Field(default='1', description="机器ID")

    class Config:
        env_prefix = ''
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'


