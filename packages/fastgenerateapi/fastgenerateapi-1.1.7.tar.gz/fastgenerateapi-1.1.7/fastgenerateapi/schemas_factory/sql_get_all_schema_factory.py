import time
from typing import Type, Optional, Union, List

from pydantic.fields import FieldInfo
from tortoise import Model
from pydantic import create_model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.data_type.mysql_data_type import mysql_data_type
from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta
from fastgenerateapi.settings.all_settings import settings


def sql_get_all_schema_factory(field_info_list, include_fields, exclude_fields) -> Optional[Type[T]]:
    """
    Is used to create a GetAllSchema
    """

    include_fields = set(include_fields) if include_fields else set()
    exclude_fields = set(exclude_fields) if exclude_fields else set()

    all_fields_info = {}
    for field_info in field_info_list:
        all_fields_info.update({
            field_info.get("COLUMN_NAME"): (
                mysql_data_type.get(field_info.get("DATA_TYPE")),
                FieldInfo(default=None, description=field_info.get("COLUMN_COMMENT"))
            )
        })
    if not include_fields:
        include_fields = set(all_fields_info.keys())

    all_fields = include_fields.difference(exclude_fields)
    if settings.app_settings.GET_EXCLUDE_ACTIVE_VALUE:
        try:
            all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
        except Exception:
            ...

    table_name = field_info_list[0].get("TABLE_NAME") if field_info_list[0] else str(time.time())
    name = table_name + "GetAllSchema"
    schema: Type[T] = create_model(
        name, **{field: all_fields_info[field] for field in all_fields}, __config__=model_config)
    return schema






