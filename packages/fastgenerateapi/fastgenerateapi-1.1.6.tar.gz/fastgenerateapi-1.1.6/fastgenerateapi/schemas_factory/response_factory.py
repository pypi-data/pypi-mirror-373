import time
from typing import Type, Union, Optional

from pydantic import create_model
from pydantic.fields import FieldInfo

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.pydantic_utils.base_model import BaseModel, model_config
from fastgenerateapi.settings.all_settings import settings


def response_factory(schema_cls: Union[Type[T], BaseModel, None] = None, name: str = "") -> Type[T]:
    fields = {}
    if settings.app_settings.CODE_RESPONSE_FIELD:
        default_code_field = FieldInfo(default=200, description="编码")
        fields.setdefault("code", (Optional[int], default_code_field))
    if settings.app_settings.SUCCESS_RESPONSE_FIELD:
        default_success_field = FieldInfo(default=True, description="是否请求成功")
        fields.setdefault("success", (Optional[bool], default_success_field))
    fields.setdefault(
        settings.app_settings.MESSAGE_RESPONSE_FIELD,
        (str, FieldInfo(default="请求成功", description="返回消息")),
    )
    if schema_cls:
        fields.setdefault(
            settings.app_settings.DATA_RESPONSE_FIELD,
            (Optional[schema_cls], FieldInfo(default={}, description="数据内容"))
        )
    else:
        fields.setdefault(
            settings.app_settings.DATA_RESPONSE_FIELD,
            (Union[dict, str, None], FieldInfo(default={}, description="数据内容"))
        )

    try:
        name = schema_cls.__name__ + name + "Response" + str(time.time())
    except:
        name = "CommonResponse"
    schema: Type[T] = create_model(name, **fields, __config__=model_config)

    return schema
