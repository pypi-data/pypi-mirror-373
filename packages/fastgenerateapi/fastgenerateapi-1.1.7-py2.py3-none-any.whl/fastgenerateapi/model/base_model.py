import datetime
import time
from typing import Optional
from tortoise import fields, models, BaseDBAsyncClient

from fastgenerateapi import my_fields


class PrimaryKeyMixin(models.Model):
    id: str = my_fields.PrimaryKeyField(pk=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.id}"


class TimestampMixin(models.Model):
    created_at: Optional[datetime.datetime] = fields.DatetimeField(null=True, auto_now_add=True, description="创建时间")
    updated_at: Optional[datetime.datetime] = fields.DatetimeField(null=True, auto_now=True, description="更新时间")

    class Meta:
        abstract = True


class BaseDeleteMixin(models.Model):
    deleted_at: Optional[int] = my_fields.SoftDeleteField()

    async def delete(self, using_db: Optional[BaseDBAsyncClient] = None) -> None:
        self.deleted_at = int(time.time() * 1000)
        await self.save(using_db=using_db)

    class Meta:
        abstract = True


class BaseActiveMixin(models.Model):
    is_active: Optional[bool] = fields.BooleanField(null=True, default=True, description="数据是否有效")

    async def delete(self, using_db: Optional[BaseDBAsyncClient] = None) -> None:
        self.is_active = False
        await self.save(using_db=using_db)

    class Meta:
        abstract = True


class TortoiseOrmAbstractModel(PrimaryKeyMixin, TimestampMixin, BaseDeleteMixin):
    ...

    class PydanticMeta:
        exclude = ["delete_at"]

    class Meta:
        abstract = True
