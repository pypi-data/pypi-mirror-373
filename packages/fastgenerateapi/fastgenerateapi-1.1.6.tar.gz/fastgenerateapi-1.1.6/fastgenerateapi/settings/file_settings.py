from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class FileServerSettings(BaseSettings):
    """
    文件配置
    """
    FILE_SERVER: Optional[str] = Field(default='http://localhost:8001', description="文件服务域名", title="file Server Domain")
    FILE_URL: Optional[str] = Field(default='/static/', description="文件路径前缀", title="file url prefix")
    FILE_ROOT: Optional[str] = Field(default='static', description="文件储存路径", title="file storage path")

    class Config:
        env_prefix = 'FileServer_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'





