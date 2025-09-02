import datetime
from typing import Optional

from pydantic.fields import FieldInfo
from tortoise import Model, fields

from common.model.base_model import TortoiseOrmAbstractModel
from fastgenerateapi import my_fields
from fastgenerateapi.my_fields.enum_field import IntEnumClass


class StaffInfo(Model):
    """
        员工信息
    """
    delete_at: Optional[datetime.datetime] = my_fields.SoftDeleteField()
    created_at: Optional[datetime.datetime] = fields.DatetimeField(null=True, auto_now_add=True, description="创建时间")
    category: Optional[IntEnumClass] = my_fields.IntEnumField(enum_list=["总经理", '主管', '员工'], description="职位分类")
    name: Optional[str] = fields.CharField(description="名字", max_length=255)
    age: Optional[int] = fields.IntField(description="年龄", default=None, null=True)
    company: fields.ForeignKeyNullableRelation["CompanyInfo"] = fields.ForeignKeyField(
        'models.CompanyInfo', related_name="staff", on_delete=fields.SET_NULL, default=None, null=True)

    @property
    def test(self):
        return "test"

    @property
    def category_name(self):
        return self.category.name

    class PydanticMeta:
        # 以下内容仅用于演示，存在重复和多余写法
        exclude = ["delete_at", "created_at"]
        get_include = ["category_name", "name"]
        get_all_include = ["company__name"]
        get_one_include = [("test", Optional[str], FieldInfo(default="", description="测试字段")), ]
        save_exclude = ["category_name", "test"]


class CompanyInfo(Model):
    """
        公司信息
    """
    delete_at: Optional[datetime.datetime] = my_fields.SoftDeleteField()
    name: str = fields.CharField(description="岗位名称", max_length=255)
    boss_name: str = fields.CharField(description="老板名字", max_length=255)
    parent: fields.ForeignKeyNullableRelation["CompanyInfo"] = fields.ForeignKeyField(
        'models.CompanyInfo',
        null=True,
        on_delete=fields.SET_NULL,
        db_constraint=False,
        description='父级')

    class PydanticMeta:
        exclude = ["delete_at"]



