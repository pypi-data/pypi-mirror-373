import importlib
from typing import List, Optional

from pydantic import BaseModel as PydanticBaseModel, BaseConfig, Field, ConfigDict

from fastgenerateapi.pydantic_utils.json_encoders import JSON_ENCODERS
from fastgenerateapi.settings.all_settings import settings

try:
    module_path, class_name = settings.app_settings.ALIAS_GENERATOR.rsplit('.', maxsplit=1)
    module = importlib.import_module(module_path)
    alias_generator = getattr(module, class_name)
except Exception:
    alias_generator = None


class ModelConfig(ConfigDict):

    def __init__(self, seq=None, **kwargs):
        default_kwargs = {
            "json_encoders": JSON_ENCODERS,
            "extra": "ignore",  # v1 ignore v2 版本没有 Extra.ignore
            # orm_mode=True,  # v1 版本
            "from_attributes": True,  # v2 版本
            # allow_population_by_field_name=True,  # v1 版本
            "populate_by_name": True,  # v2 版本,支持原本的属性和驼峰命名
            "alias_generator": alias_generator,
        }
        default_kwargs.update(kwargs)
        super().__init__(seq=seq, **default_kwargs)


model_config = ConfigDict(
    json_encoders=JSON_ENCODERS,
    extra="ignore",  # v1 ignore v2 版本没有 Extra.ignore
    # orm_mode=True,  # v1 版本
    from_attributes=True,  # v2 版本
    # allow_population_by_field_name=True,  # v1 版本
    populate_by_name=True,  # v2 版本,支持原本的属性和驼峰命名
    alias_generator=alias_generator,
)


# class Config(BaseConfig):
#     json_encoders = JSON_ENCODERS
#     extra = "ignore"  # v1 ignore v2 版本没有 Extra.ignore
#     orm_mode = True  # v1 版本
#     from_attributes = True  # v2 版本
#     allow_population_by_field_name = True  # v1 版本
#     populate_by_name = True  # v2 版本,支持原本的属性和驼峰命名
#     alias_generator = alias_generator


class BaseModel(PydanticBaseModel):
    model_config = model_config


class IdList(BaseModel):
    id_list: List[str] = Field([], description="id数组")


class EmptyPydantic(BaseModel):
    ...


class SearchPydantic(BaseModel):
    search: Optional[str] = Field(None, description="搜索")
