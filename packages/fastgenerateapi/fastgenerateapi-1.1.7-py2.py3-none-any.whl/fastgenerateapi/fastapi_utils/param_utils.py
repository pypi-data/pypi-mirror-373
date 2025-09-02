# 用于解决依赖中使用Query、Path等参数时，无法获取相关信息的问题

from typing import List, Optional

import fastapi
from fastapi import params
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_sub_dependant


def get_param_sub_dependant(
        *,
        param_name: str,
        depends: params.Depends,
        path: str,
        security_scopes: Optional[List[str]] = None,
) -> Dependant:
    assert depends.dependency
    dependant = get_sub_dependant(
        depends=depends,
        dependency=depends.dependency,
        path=path,
        name=param_name,
        security_scopes=security_scopes,
    )
    for query_param in dependant.query_params:
        query_param_field = depends.dependency.model_fields.get(query_param.name)
        if query_param_field:
            query_param.field_info.description = query_param_field.description or query_param_field.title or ""
        else:
            query_param.field_info.description = query_param_field.description or query_param_field.title or ""
    return dependant


fastapi.dependencies.utils.get_param_sub_dependant = get_param_sub_dependant


