import inspect
from typing import Type, Union, List, Optional

from fastgenerateapi.settings.all_settings import settings
from tortoise import Model


class DBModelMixin:
    others_description = {
        "gt": "大于",
        "gte": "大于等于",
        "lt": "小于",
        "lte": "小于等于",
        "contains": "模糊搜索",
        "in": "范围",
    }

    @staticmethod
    def _get_pk_field(model_class: Type[Model]) -> str:
        try:
            return model_class.describe()["pk_field"]["db_column"]
        except:
            return "id"

    @staticmethod
    def get_field_description(model_class: Type[Model], fields: Union[str, list, tuple, set]) -> str:
        if fields in ["id", "pk"]:
            return "主键"
        if type(fields) == str:
            try:
                field_info = model_class._meta.fields_map.get(fields)
                field_info_fk = model_class._meta.fields_map.get(fields.rstrip("_id"))
                if field_info:
                    return field_info.description or ""
                elif fields.endswith("_id") and field_info_fk:
                    return field_info_fk.description or ""
                elif "__" in fields:
                    field_list = fields.split("__", maxsplit=1)
                    description = ""
                    description += DBModelMixin.get_field_description(model_class=model_class, fields=field_list[0])
                    if field_list[1] in DBModelMixin.others_description:
                        description += DBModelMixin.get_field_description(
                            model_class=model_class,
                            fields=field_list[1]
                        )
                    else:
                        description += DBModelMixin.get_field_description(
                            model_class=DBModelMixin._get_foreign_key_relation_class(model_class=model_class, field=field_list[0]),
                            fields=field_list[1]
                        )
                    return description
                else:
                    return DBModelMixin.others_description.get(fields, "")

            except Exception:
                return fields
        else:
            try:
                description_list = []
                for field in fields:
                    description_list.append(DBModelMixin.get_field_description(model_class=model_class, fields=field))
                return ",".join(description_list)

            except Exception:
                return ",".join(list(fields))

    @staticmethod
    def get_model_description(model_class: Optional[Type[Model]]) -> str:
        return model_class._meta.table_description or model_class.__name__

    @staticmethod
    def get_model_prefix_name(model_class: Type[Model]) -> str:
        model_strike_name = model_class.__name__[0]
        for name in model_class.__name__[1:]:
            if name.isupper():
                model_strike_name += f"-{name}"
            else:
                model_strike_name += name
        if settings.app_settings.ROUTER_WHETHER_UNDERLINE_TO_STRIKE:
            return model_strike_name.lower()
        return model_strike_name.lower().replace("-", "_")

    @staticmethod
    def _get_unique_fields(model_class: Type[Model] = None, exclude_pk: bool = True) -> List[str]:
        try:
            if exclude_pk:
                _pk = DBModelMixin._get_pk_field(model_class=model_class)
                return [key for key, value in model_class._meta.fields_map.items() if value.unique and key != _pk]
            return [key for key, value in model_class._meta.fields_map.items() if value.unique]
        except:
            return []

    @staticmethod
    def _get_foreign_key_fields(model_class: Type[Model] = None, is_with_id: bool = True) -> List[str]:
        try:
            fields = list(model_class._meta.fk_fields)
            if is_with_id:
                fields = [field + "_id" for field in fields]
            return fields
        except:
            return []

    @staticmethod
    def _get_unique_together_fields(model_class: Type[Model] = None) -> tuple:
        try:
            return model_class._meta.unique_together
        except:
            return tuple()

    @staticmethod
    def _get_foreign_key_relation_class(model_class: Type[Model], field: str) -> Type[Model]:
        try:
            module = inspect.getmodule(model_class, inspect.getfile(model_class))
            res_class = getattr(module, model_class._meta.fields_map.get(field).model_name.split(".")[1])
            return res_class
        except:
            return model_class

