from typing import Optional, Union, Type

from fastapi import Depends, Query
from pydantic import create_model
from pydantic.fields import FieldInfo

from fastgenerateapi.pydantic_utils.base_model import BaseModel, model_config
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.str_util import parse_str_to_int, parse_str_to_bool


def paginator_deps():
    """
    Created the pagination dependency to be used in the router
    """
    # fields = {
    #     settings.app_settings.CURRENT_PAGE_FIELD: (
    #         Union[None, str, int],
    #         FieldInfo(default=1, description="当前页")
    #     ),
    #     settings.app_settings.PAGE_SIZE_FIELD: (
    #         Union[None, str, int],
    #         FieldInfo(default=settings.app_settings.DEFAULT_PAGE_SIZE,  description="每页数量")
    #     ),
    #     settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD: (
    #         Union[None, str, bool, int],
    #         FieldInfo(default=settings.app_settings.DEFAULT_WHETHER_PAGE, description="是否分页")
    #     ),
    # }

    fields = {
        settings.app_settings.CURRENT_PAGE_FIELD: (
            Union[None, str, int],
            FieldInfo(default=Query(1), title="当前页", description="当前页")
        ),
        settings.app_settings.PAGE_SIZE_FIELD: (
            Union[None, str, int],
            FieldInfo(default=Query(settings.app_settings.DEFAULT_PAGE_SIZE), title="每页数量", description="每页数量")
        ),
        settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD: (
            Union[None, str, bool, int],
            FieldInfo(default=Query(settings.app_settings.DEFAULT_WHETHER_PAGE), title="是否分页", description="是否分页")
        ),
    }
    pagination_model: Type[BaseModel] = create_model("paginator", **fields, __config__=model_config)

    def pagination_deps(paginator: pagination_model = Depends(pagination_model)) -> pagination_model:
        current_page_value = parse_str_to_int(getattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD))
        page_size_value = parse_str_to_int(getattr(paginator, settings.app_settings.PAGE_SIZE_FIELD))
        whether_page_value = parse_str_to_bool(getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD))
        if current_page_value <= 0:
            setattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD, 1)
        else:
            setattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD, current_page_value)
        if page_size_value <= 0:
            setattr(paginator, settings.app_settings.PAGE_SIZE_FIELD, settings.app_settings.DEFAULT_PAGE_SIZE)
        elif page_size_value > settings.app_settings.DEFAULT_MAX_PAGE_SIZE:
            setattr(paginator, settings.app_settings.PAGE_SIZE_FIELD, settings.app_settings.DEFAULT_MAX_PAGE_SIZE)
        else:
            setattr(paginator, settings.app_settings.PAGE_SIZE_FIELD, page_size_value)
        setattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD, whether_page_value)

        return paginator

    return pagination_deps


