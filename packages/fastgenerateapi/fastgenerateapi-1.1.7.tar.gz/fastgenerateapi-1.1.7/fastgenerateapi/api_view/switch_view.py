from typing import List, Any

from fastapi.types import DecoratedCallable
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.schemas_factory import response_factory, get_one_schema_factory
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND
from fastgenerateapi.utils.str_util import parse_str_to_bool


class SwitchView(BaseView):

    switch_route_fields: List[str] = None  # 布尔值|枚举值切换路由
    """
    # 生成一个路由： .../is_enabled/{pk}  方法：PUT
    # 无参数： 默认布尔值类型切换相反值    有参数：{"is_enabled":True} 切换参数值
    switch_route_fields = ["is_enabled", "status", ...]
    """

    async def switch(self, pk, request, filed, *args, **kwargs):
        try:
            request_data = await request.json()
        except Exception:
            request_data = {}

        model = await self.queryset.filter(id=pk).first()
        if not model:
            raise NOT_FOUND

        setattr(
            model,
            filed,
            not getattr(model, filed) if request_data.get(filed) is None else request_data.get(filed)
        )

        await model.save()

        await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields)

        # await self.setattr_model_rpc(self.rpc_class, model, self.rpc_param)

        return self.get_one_schema.from_orm(model)

    def _switch_decorator(self, filed, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(pk: str, request: Request) -> JSONResponse:
            data = await self.switch(pk=pk, request=request, filed=filed, *args, **kwargs)
            return self.success(data=data)
        return route

    def _handler_switch_route_settings(self):
        if not self.switch_route_fields:
            return
        if not hasattr(self, "get_one_schema"):
            self.get_one_schema = get_one_schema_factory(model_class=self.model_class)
        if not hasattr(self, "get_one_response_schema"):
            self.get_one_response_schema = response_factory(self.get_one_schema, name="GetOne")
        for switch_route_field in self.switch_route_fields:
            if self.model_class._meta.fields_map.get(switch_route_field).field_type not in [bool, int]:
                self.error(msg=f"{switch_route_field} is not bool or int")
            # 待增加数据库模型description的读取
            summary = f"Switch {switch_route_field}"
            self._add_api_route(
                path="/%s/{pk}" % ("switch_"+switch_route_field),
                endpoint=self._switch_decorator(switch_route_field),
                methods=["PUT"],
                response_model=self.get_one_response_schema,
                summary=summary,
                dependencies=True,
                error_responses=[NOT_FOUND],
            )


