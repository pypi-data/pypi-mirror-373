from typing import Optional, Type, Any, Union

from fastapi import Query, Depends
from fastapi.types import DecoratedCallable
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.data_type.data_type import CALLABLE, DEPENDENCIES
from fastgenerateapi.deps import filter_params_deps
from fastgenerateapi.schemas_factory import response_factory
from fastgenerateapi.settings.all_settings import settings


class DeleteFilterView(BaseView):

    delete_filter_route: Union[bool, DEPENDENCIES] = True
    """
    必须继承 GetAllView 才能使用
    与 GetAllView 同步的筛选条件
    """

    @atomic()
    async def destroy_filter(self, search: str, filters: dict, *args, **kwargs):
        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)

        await self.delete_queryset(queryset)

        return

    def _delete_filter_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request: Request,
                search: str = Query(default="", description="搜索"),
                filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields)),
        ) -> JSONResponse:
            await self.destroy_filter(
                search=search,
                filters=filters,
                request=request,
                *args, **kwargs
            )
            return self.success(msg="删除成功")
        return route

    def _handler_destroy_filter_settings(self):
        if self.delete_filter_route:
            return
        if not hasattr(self, "get_one_response_schema"):
            self.get_one_response_schema = response_factory(None, name="GetOne")
        doc = self.destroy_filter.__doc__
        summary = doc.strip().split("\n")[0] if doc else "Delete Filter"
        path = f"/{settings.app_settings.ROUTER_FILTER_DELETE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._delete_filter_decorator(),
            methods=["DELETE"],
            response_model=Optional[self.get_one_response_schema],
            summary=summary,
            dependencies=self.delete_filter_route,
        )





