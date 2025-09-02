from typing import Type, Any, Optional

from fastapi import Depends, Query
from pydantic.fields import FieldInfo

from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.pydantic_utils.base_model import ModelConfig
from fastgenerateapi.settings.all_settings import settings

from pydantic import BaseModel, create_model


def tree_params_deps():
    """
        生成 tree 开始筛选字段的依赖
    """

    model_fields = {
        settings.app_settings.DEFAULT_TREE_FILTER_FIELD: (
            Optional[str],
            FieldInfo(
                title=f"{settings.app_settings.DEFAULT_TREE_FILTER_FIELD}",
                default=Query(""),
                description="起始节点ID"
            )
        )
    }

    filter_tree_params_model: Type[BaseModel] = create_model("TreeFilterParams", __config__=model_config, **model_fields)

    def filter_query(filter_params: filter_tree_params_model = Depends(filter_tree_params_model)) -> Optional[str]:
        """
            filter 筛选字段依赖
        :param filter_params:
        :return:
        """
        result = getattr(filter_params, settings.app_settings.DEFAULT_TREE_FILTER_FIELD, None)

        return result or None

    return filter_query


