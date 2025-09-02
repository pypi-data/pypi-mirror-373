import time
from typing import Type, Optional, Union, List

from pydantic.fields import FieldInfo
from tortoise import Model
from pydantic import create_model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta
from fastgenerateapi.settings.all_settings import settings


def get_all_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
        name: Optional[str] = None
) -> Optional[Type[T]]:
    """
    Is used to create a GetAllSchema
    """
    if not hasattr(model_class, "PydanticMeta"):
        return None
    if not hasattr(model_class.PydanticMeta, "get_all_include") and not hasattr(model_class.PydanticMeta, "get_all_exclude"):
        return None

    all_fields_info = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()

    if hasattr(model_class.PydanticMeta, "include"):
        include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    else:
        include_fields.update(all_fields_info.keys())
    if hasattr(model_class.PydanticMeta, "exclude"):
        exclude_fields.update(model_class.PydanticMeta.exclude)

    if hasattr(model_class.PydanticMeta, "get_include"):
        get_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_include)
        all_fields_info.update(get_include_fields_dict)
        include_fields.update(get_include_fields_dict.keys())
    if hasattr(model_class.PydanticMeta, "get_exclude"):
        exclude_fields.update(model_class.PydanticMeta.get_exclude)

    # get_all_include
    if hasattr(model_class.PydanticMeta, "get_all_include"):
        get_all_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_all_include)
        all_fields_info.update(get_all_include_fields_dict)
        include_fields.update(get_all_include_fields_dict.keys())
    # get_all_exclude
    if hasattr(model_class.PydanticMeta, "get_all_exclude"):
        exclude_fields.update(model_class.PydanticMeta.get_all_exclude)

    # 参数处理
    if include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if extra_include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, extra_include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if exclude:
        exclude_fields.update(exclude)

    all_fields = include_fields.difference(exclude_fields)
    if settings.app_settings.GET_EXCLUDE_ACTIVE_VALUE:
        try:
            all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
        except Exception:
            ...

    schema_name = name if name else model_class.__name__ + "GetAllSchema"
    schema: Type[T] = create_model(
        schema_name, **{field: all_fields_info[field] for field in all_fields}, __config__=model_config)
    return schema


def get_list_schema_factory(schema_cls: Type[T] = None) -> Type[T]:
    if schema_cls:
        fields = {
            settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List[schema_cls]], FieldInfo(default=[], description="数据返回")),
        }
        name = schema_cls.__name__ + "GetListSchema"
    else:
        fields = {
            settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List], FieldInfo(default=[], description="数据返回")),
        }
        name = "GetListSchema" + str(time.time())
    schema: Type[T] = create_model(name, **fields, __config__=model_config)
    return schema


def get_page_schema_factory(schema_cls: Type[T] = None) -> Type[T]:
    fields = {
        settings.app_settings.CURRENT_PAGE_FIELD: (Optional[int], FieldInfo(default=1, description="当前页")),
        settings.app_settings.PAGE_SIZE_FIELD: (Optional[int], FieldInfo(default=settings.app_settings.DEFAULT_PAGE_SIZE, description="每页数量")),
        settings.app_settings.TOTAL_SIZE_FIELD: (Optional[int], FieldInfo(default=0, description="数量总计")),
    }
    if schema_cls:
        fields.update({settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List[schema_cls]], FieldInfo(default=[], description="数据返回"))})
        name = schema_cls.__name__ + "GetPageSchema"
    else:
        fields.update({settings.app_settings.LIST_RESPONSE_FIELD: (Optional[List], FieldInfo(default=[], description="数据返回"))})
        name = "GetPageSchema" + str(time.time())
    schema: Type[T] = create_model(name, **fields, __config__=model_config)
    return schema






