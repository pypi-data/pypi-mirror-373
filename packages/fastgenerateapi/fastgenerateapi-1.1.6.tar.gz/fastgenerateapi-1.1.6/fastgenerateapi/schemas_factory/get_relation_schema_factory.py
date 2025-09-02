from typing import Type, Optional, Union, List

from fastgenerateapi.schemas_factory.get_one_schema_factory import get_one_schema_factory
from pydantic.fields import FieldInfo
from tortoise import Model
from pydantic import create_model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta
from fastgenerateapi.settings.all_settings import settings


def get_relation_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
        name: Optional[str] = None
) -> Optional[Type[T]]:
    """
    Is used to create a GetRelationSchema
    """
    all_fields_info: dict = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()
    if hasattr(model_class, "PydanticMeta"):
        if hasattr(model_class.PydanticMeta, "get_relation_include"):
            get_tree_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_tree_include)
            all_fields_info.update(get_tree_include_fields_dict)
            include_fields.update(get_tree_include_fields_dict.keys())
        if hasattr(model_class.PydanticMeta, "include"):
            include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.include)
            all_fields_info.update(include_fields_dict)
            include_fields.update(include_fields_dict.keys())
        else:
            include_fields.update(all_fields_info.keys())
        if hasattr(model_class.PydanticMeta, "get_relation_exclude"):
            exclude_fields.update(model_class.PydanticMeta.get_tree_exclude)
        if hasattr(model_class.PydanticMeta, "exclude"):
            exclude_fields.update(model_class.PydanticMeta.exclude)
    else:
        include_fields.update(all_fields_info.keys())

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

    schema_name = name if name else model_class.__name__ + "GetRelationSchema"
    schema: Type[T] = create_model(
        schema_name, **{field: all_fields_info[field] for field in all_fields}, __config__=model_config)

    return schema










