import time
from typing import Optional, Type, Any, Union

from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.data_type.data_type import CALLABLE, DEPENDENCIES
from fastgenerateapi.pydantic_utils.base_model import IdList
from fastgenerateapi.schemas_factory import response_factory
from fastgenerateapi.settings.all_settings import settings


class DeleteView(BaseView):

    delete_route: Union[bool, DEPENDENCIES] = True
    delete_schema: Optional[Type[BaseModel]] = IdList
    """
    delete_route: 删除路由开关，可以放依赖函数列表
    delete_schema: 删除请求模型
    """

    @atomic()
    async def destroy(self, request_data, *args, **kwargs):
        queryset = await self.get_del_queryset(request_data=request_data, *args, **kwargs)
        await self.delete_queryset(queryset)

        return

    # 弃用思路：唯一字段加时间戳
    # if unique_fields := self._get_unique_fields(self.model_class):
    #     for model in await queryset:
    #         model.is_active = False
    #         for field in unique_fields:
    #             try:
    #                 setattr(model, field, getattr(model, field) + f"__{int(time.time() * 1000)}")
    #             except Exception as e:
    #                 setattr(model, field, getattr(model, field) + f"__{int(time.time() * 1000)}")
    #         await model.save()
    # else:
    #     await queryset.update(is_active=False)

    async def get_del_queryset(self, request_data, *args, **kwargs):
        queryset = self.queryset.filter(id__in=request_data.id_list)
        return queryset

    def _delete_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request_data: self.delete_schema,  # type: ignore
                request: Request,
        ) -> JSONResponse:
            await self.destroy(
                request_data=request_data,
                request=request,
                *args, **kwargs
            )
            return self.success(msg="删除成功")
        return route

    def _handler_delete_settings(self):
        if not self.delete_route:
            return
        if not hasattr(self, "get_one_response_schema"):
            self.get_one_response_schema = response_factory(None, name="GetOne")
        doc = self.destroy.__doc__
        summary = doc.strip().split("\n")[0] if doc else "Delete All"
        path = f"/{settings.app_settings.ROUTER_DELETE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._delete_decorator(),
            methods=["DELETE"],
            response_model=Optional[self.get_one_response_schema],
            summary=summary,
            dependencies=self.delete_route,
        )





