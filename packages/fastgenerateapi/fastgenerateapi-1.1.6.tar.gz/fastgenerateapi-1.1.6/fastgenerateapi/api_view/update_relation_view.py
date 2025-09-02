from typing import Optional, Type, Union, Any

from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.expressions import Q
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.save_mixin import SaveMixin
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.pydantic_utils.base_model import IdList
from fastgenerateapi.schemas_factory import response_factory
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND


class UpdateRelationView(BaseView, SaveMixin):

    path_id_name: str
    relation_id_name: str
    update_relation_schema: Optional[Type[BaseModel]] = IdList
    update_relation_route: Union[bool, DEPENDENCIES] = True
    """
    path_id_name: 路径id在模型中对应的字段名
    relation_id_name: 模型中需要修改的字段名
    update_relation_schema: 修改请求模型
    update_relation_route: 修改路由开关，可以放依赖函数列表
    """

    @atomic()
    async def update_relation(self, pk: str, request_data, *args, **kwargs):
        active_id_list = set(await self.queryset.filter(eval(f"Q({self.path_id_name}='{pk}')")).values_list(
            self._get_pk_field(model_class=self.model_class), flat=True
        ))
        add_id_list = set(request_data.id_list) - active_id_list
        delete_id_list = active_id_list - set(request_data.id_list)
        if len(add_id_list) > 0:
            relation_list = []
            for add_id in add_id_list:
                add_dict = {
                    self.path_id_name: pk,
                    self.relation_id_name: add_id
                }
                relation_list.append(self.model_class(**add_dict))
            await self.model_class.bulk_create(relation_list)
        if len(delete_id_list) > 0:
            await self.model_class.filter(id__in=delete_id_list).delete()

        return

    def _update_relation_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                pk: str,
                request_data: self.update_relation_schema,  # type: ignore
                request: Request,
        ) -> JSONResponse:
            await self.update_relation(
                pk=pk,
                request_data=request_data,
                request=request,
                *args, **kwargs
            )
            return self.success()
        return route

    def _handler_update_relation_settings(self):
        if not self.update_relation_route:
            return
        self.update_relation_response_schema = response_factory(name="UpdateRelation")
        doc = self.update_relation.__doc__
        summary = doc.strip().split("\n")[0] if doc else f"Update {self.model_class.__name__.title()}"
        path = f"/update-{self.relation_id_name.strip('_id')}-by-{self.path_id_name.strip('_id')}/{'{pk}'}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else "/{pk}"
        self._add_api_route(
            path=path,
            endpoint=self._update_relation_decorator(),
            methods=["PUT"],
            response_model=self.update_relation_response_schema,
            summary=summary,
            dependencies=self.update_relation_route,
            error_responses=[NOT_FOUND],
        )



