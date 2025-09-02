from typing import Type, Union, Any, Optional

from fastapi import Depends, Query
from pydantic import create_model
from tortoise import Model

from fastgenerateapi.controller.filter_controller import BaseFilter
from fastgenerateapi.data_type.data_type import PYDANTIC_SCHEMA
from fastgenerateapi.pydantic_utils.base_model import EmptyPydantic, SearchPydantic
from fastgenerateapi.schemas_factory.filter_schema_factory import filter_schema_factory


def search_params_deps(fields: Optional[list[str]] = None):
    """
    目的：当 fields 为空时，不会生成search的文档
    :param fields:
    :return:
    """
    if not fields:
        filter_schema_dep = EmptyPydantic
    else:
        filter_schema_dep = SearchPydantic

    def filter_search(search_params: filter_schema_dep = Depends()):
        return getattr(search_params, "search", "")

    return filter_search


def filter_params_deps(
        model_class: Type[Model],
        fields: Optional[list[str, tuple[str, Type], BaseFilter]] = None,
        schema: Optional[PYDANTIC_SCHEMA] = None
):
    """
        生成filter依赖
    """
    filter_schema_dep = schema or EmptyPydantic
    filter_params_model = filter_schema_factory(model_class, fields)

    def filter_query(
            filter_params: filter_params_model = Depends(),
            filter_schema: filter_schema_dep = Depends(),
    ) -> dict[str, Any]:
        """
            filter 筛选字段依赖
        :param filter_params:
        :param filter_schema:
        :return:
        """
        result = filter_params.dict(exclude_none=True)
        result.update(filter_schema.dict(exclude_none=True))
        return result

    return filter_query
