from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    """
        Database Settings
    """

    TYPE: Optional[str] = Field(default='mysql', description="数据库类型")
    HOST: Optional[str] = Field(default='127.0.0.1', description="数据库域名")
    PORT: Optional[str] = Field(default='3306', description="数据库端口")
    DATABASE: Optional[str] = Field(default='admin', description="数据库名")
    USERNAME: Optional[str] = Field(default='root', description="数据库用户名")
    PASSWORD: Optional[str] = Field(default='', description="数据库密码")

    @property
    def dsn(self):
        return f"{self.TYPE.lower()}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"

    class Config:
        env_prefix = 'DB_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'


class PostgresqlSettings(DBSettings):
    """
        Postgresql Settings
    """
    TYPE: Optional[str] = Field(default='postgres', description="数据库类型")

    class Config:
        env_prefix = 'Postgresql_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'


class MySQLSettings(DBSettings):
    """
        MySQL Settings
    """

    class Config:
        env_prefix = 'MYSQL_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'


class LocalSettings(DBSettings):
    """
        MySQL Settings
    """
    TYPE: str = Field(..., description="数据库类型")

    class Config:
        env_prefix = 'LOCAL_'
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'




