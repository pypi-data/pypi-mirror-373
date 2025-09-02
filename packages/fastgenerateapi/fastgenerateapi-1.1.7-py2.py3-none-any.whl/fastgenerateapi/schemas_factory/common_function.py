from typing import Type, Optional, Union

from pydantic import validator
from pydantic.fields import FieldInfo
from tortoise import Model

from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.settings.all_settings import settings


def get_field_info(value, description="", default_field_type=None) -> (Type, FieldInfo):
    if value.pk:
        return str, FieldInfo()
    if value.field_type is None:
        if default_field_type:
            field_type = Optional[default_field_type]
        else:
            field_type = Optional[str]
    else:
        if hasattr(value, "null") and value.null:
            field_type = Optional[value.field_type]
        else:
            field_type = value.field_type
    field_info_dict = {}
    if hasattr(value, "default") and not hasattr(value.default, '__call__'):
        field_info_dict.setdefault("default", value.default)
    if hasattr(value, "description"):
        field_info_dict.setdefault("description", description + (value.description or ""))
    if hasattr(value, "alias"):
        field_info_dict.setdefault("alias", value.alias)
    if hasattr(value, "gt"):
        field_info_dict.setdefault("gt", value.gt)
    if hasattr(value, "ge"):
        field_info_dict.setdefault("ge", value.ge)
    if hasattr(value, "lt"):
        field_info_dict.setdefault("lt", value.lt)
    if hasattr(value, "le"):
        field_info_dict.setdefault("le", value.le)
    if hasattr(value, "min_length"):
        field_info_dict.setdefault("min_length", value.min_length)
    if hasattr(value, "max_length"):
        field_info_dict.setdefault("max_length", value.max_length)
    if hasattr(value, "regex"):
        field_info_dict.setdefault("regex", value.regex)
    return field_type, FieldInfo(**field_info_dict)


def get_dict_from_model_fields(model_class: Type[Model]) -> dict:
    all_fields_info = {}
    default_field_type = model_class._meta.fields_map.get("id").field_type
    for key, value in model_class._meta.fields_map.items():
        if key in model_class._meta.fk_fields:
            key += "_id"
        all_fields_info[key] = get_field_info(value, default_field_type=default_field_type)

    return all_fields_info


def get_field_info_from_model_class(model_class: Type[Model], field: str, description="") -> (Type, FieldInfo):
    if "__" not in field:
        value = model_class._meta.fields_map.get(field)
        if not value:
            return Optional[str], FieldInfo(default=None, description=f"{field}")
        return get_field_info(value, description=description)

    field_info = model_class._meta.fields_map.get(field.split("__", maxsplit=1)[0])
    if field_info:
        description += field_info.description or ""

    model_class = DBModelMixin._get_foreign_key_relation_class(model_class, field.split("__", maxsplit=1)[0])

    return get_field_info_from_model_class(model_class, field.split("__", maxsplit=1)[1], description)


def get_dict_from_pydanticmeta(model_class: Type[Model], data: Union[list, tuple, set]):
    fields_info = {}
    if not data:
        return fields_info
    for field in data:
        if isinstance(field, str):
            key_field = field
            field_type, field_info = get_field_info_from_model_class(model_class, field)
            if settings.app_settings.SCHEMAS_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE:
                key_field = key_field.replace("__", "_")
            fields_info.setdefault(key_field, (field_type, field_info))
        elif isinstance(field, tuple):
            key_field = field[0]
            field_type, field_info = get_field_info_from_model_class(model_class, field[0])
            if len(field) == 2:
                if isinstance(field[1], str):
                    key_field = field[1]
                else:
                    field_type = field[1]
            elif len(field) == 3:
                if isinstance(field[1], str):
                    key_field = field[1]
                    if isinstance(field[2], FieldInfo):
                        field_info = field[2]
                    else:
                        field_type = field[2]
                else:
                    field_type = field[1]
                    field_info = field[2]
            elif len(field) > 3:
                key_field = field[1]
                field_type = field[2]
                field_info = field[3]
            fields_info.setdefault(key_field, (field_type, field_info))
        else:
            raise NotImplemented
    return fields_info


def get_validate_dict_from_fields(fields_info: dict) -> dict:
    validator_dict = {}

    def remove_blank_strings(v, values):
        if isinstance(v, str):
            v = v.strip()
        if v == "":
            return None
        return v

    for filed, field_tuple in fields_info.items():
        if field_tuple[0] == str:
            method_name = "check_%s" % filed
            validator_method = validator(filed, pre=True, allow_reuse=True)(remove_blank_strings)
            validator_dict[method_name] = validator_method
    return validator_dict


