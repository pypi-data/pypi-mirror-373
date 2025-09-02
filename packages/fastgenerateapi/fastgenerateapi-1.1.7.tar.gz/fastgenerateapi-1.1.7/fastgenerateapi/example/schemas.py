from typing import List, Optional

from pydantic import validator
from tortoise.contrib.pydantic import pydantic_model_creator

from fastgenerateapi.pydantic_utils.base_model import BaseModel
from fastgenerateapi.schemas_factory import get_all_schema_factory
from fastgenerateapi.schemas_factory.common_schema_factory import common_schema_factory
from fastgenerateapi.example.models import CompanyInfo, StaffInfo


# 方式一：解决了方式二存在的问题
# get_one 可以使用 get_one_schema_factory()
# 其他方法，例如 get_all 需要model有对应的 get_all_include 或者 get_all_exclude 可使用 get_all_schema_factory()
# 否则统一使用 common_schema_factory()

class StaffReadSchema(common_schema_factory(
    StaffInfo,
    name="StaffReadSchema",
    extra_include=["test"],
)):
    test_name: Optional[str]

    @validator("test")
    def check_test(cls, value):
        if value == "test":
            return "test11"
        return value


# 方式二：使用 pydantic 写法 继承model
#  存在问题：
#       1， 外键默认需要自己添加
#       2， 关联表字段需要自己添加
#       3， 必填字符串字段参数为空时，schema和model校验都不会报错

class CompanyInfoRead(BaseModel, pydantic_model_creator(
    CompanyInfo,
    name='CompanyInfoRead',
)):
    ...


class CompanyInfoCreate(BaseModel, pydantic_model_creator(
    CompanyInfo,
    name='CompanyInfoCreate',
    exclude_readonly=True,
)):
    ...


# 方式三：完全自己写

class TestSchema(BaseModel):
    name: str


class ListTestSchema(BaseModel):
    list: List[TestSchema]
