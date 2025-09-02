from typing import Union, Optional, Type, cast, List, Any, Callable, Coroutine

from fastapi import Depends, Query
from fastapi.types import DecoratedCallable
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.get_mixin import GetMixin
from fastgenerateapi.cache.cache_decorator import get_all_cache_decorator
from fastgenerateapi.cache.key_builder import generate_key_builder
from fastgenerateapi.controller import SearchController, BaseFilter, FilterController
from fastgenerateapi.data_type.data_type import DEPENDENCIES, PYDANTIC_SCHEMA
from fastgenerateapi.deps import paginator_deps, filter_params_deps
from fastgenerateapi.deps.filter_params_deps import search_params_deps
from fastgenerateapi.schemas_factory import get_all_schema_factory, get_page_schema_factory, get_one_schema_factory, \
    response_factory
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory
from fastgenerateapi.settings.all_settings import settings


class GetAllView(BaseView, GetMixin):
    get_all_route: Union[bool, DEPENDENCIES] = True
    get_all_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    search_fields: Union[None, list] = None
    filter_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    filter_fields: Union[None, list] = None
    order_by_fields: Union[None, list] = None
    """
    get_all_route: 获取详情路由开关，可以放依赖函数列表
    get_all_schema: 返回序列化
        优先级：  
            - 1：get_all_schema:传入参数
            - 2：模型层get_all_include和get_all_exclude(同时存在交集)
            - 3：get_one_schemas
    search_fields: search搜索对应字段 
        example：("name__contains", str, "name") 类型是str的时候可以省略，没有第三个值时，自动双下划线转单下划线
    filter_fields: 筛选对应字段
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
    order_by_fields: 排序对应字段
    """

    async def get_all(self, search: Optional[str], filters: dict, *args, **kwargs) -> Union[BaseModel, dict, None]:
        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)

        return await self.pagination_data(queryset=queryset, *args, **kwargs)

    async def get_queryset(self, search: Optional[str], filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理search搜索；处理筛选字段；处理外键预加载；处理排序
        """
        queryset = self.search_controller.query(queryset=self.queryset, value=search)
        queryset = await self.filter_queryset(queryset, filters)
        queryset = self.filter_controller.query(queryset=queryset, values=filters)
        queryset = queryset.prefetch_related(*self.prefetch_related_fields.keys())
        if self.order_by_fields:
            queryset = queryset.order_by(*self.order_by_fields, "id")
        else:
            queryset = queryset.order_by("id")

        return queryset

    async def filter_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def set_get_all_model(self, model: Model) -> Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    async def pagination_data(
            self,
            queryset: QuerySet,
            paginator=None,
            schema: Type[BaseModel] = None,
            fields: List[Union[str, tuple]] = None,
            *args, **kwargs
    ):

        data_list = []
        if paginator is None or getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == \
                settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
            model_list = await queryset.all()
        else:
            count = await queryset.count()
            current_num = getattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD)
            page_size = getattr(paginator, settings.app_settings.PAGE_SIZE_FIELD)
            queryset = queryset.offset(cast(int, (current_num - 1) * page_size))
            model_list = await queryset.limit(page_size)

        for model in model_list:

            await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields, *args, **kwargs)

            # await self.setattr_model_rpc(self.rpc_class, model, self.rpc_param)
            model = await self.set_get_model(model)
            model = await self.set_get_all_model(model)

            if schema:
                data_list.append(schema.from_orm(model))
            elif fields:
                data_list.append(await self.getattr_model(model=model, fields=fields))
            else:
                data_list.append(self.get_all_schema.from_orm(model))

        if paginator is None or getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == \
                settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
            if schema or fields:
                return get_list_schema_factory()(**{settings.app_settings.LIST_RESPONSE_FIELD: data_list})
            return self.get_list_schema(**{settings.app_settings.LIST_RESPONSE_FIELD: data_list})
        if schema or fields:
            return get_page_schema_factory()(**{
                settings.app_settings.CURRENT_PAGE_FIELD: current_num,
                settings.app_settings.PAGE_SIZE_FIELD: page_size,
                settings.app_settings.TOTAL_SIZE_FIELD: count,
                settings.app_settings.LIST_RESPONSE_FIELD: data_list,
            })
        return self.get_page_schema(**{
            settings.app_settings.CURRENT_PAGE_FIELD: current_num,
            settings.app_settings.PAGE_SIZE_FIELD: page_size,
            settings.app_settings.TOTAL_SIZE_FIELD: count,
            settings.app_settings.LIST_RESPONSE_FIELD: data_list,
        })

    def get_page_list(self, page_result: BaseModel):
        return getattr(page_result, settings.app_settings.LIST_RESPONSE_FIELD, [])

    def _get_all_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        @get_all_cache_decorator(cache(expire=settings.app_settings.CACHE_GET_ALL_SECONDS, coder=JsonCoder,
                                       key_builder=generate_key_builder))
        async def route(
                request: Request,
                paginator=Depends(paginator_deps()),
                search: Optional[str] = Depends(search_params_deps(self.search_fields)),
                filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields, schema=self.filter_schema)),
        ) -> JSONResponse:
            data = await self.get_all(
                paginator=paginator,
                search=search,
                filters=filters,
                request=request,
                *args,
                **kwargs
            )
            return self.success(data=data)

        return route

    def _handler_get_all_settings(self):
        if not self.get_all_route:
            return
        self.search_controller = SearchController(self.get_base_filter(self.search_fields))
        self.filter_controller = FilterController(self.get_base_filter(self.filter_fields, self.filter_schema))
        self.get_all_schema = self.get_all_schema or get_all_schema_factory(
            self.model_class) or self.get_one_schema if hasattr(self, "get_one_schema") else get_one_schema_factory(
            self.model_class)
        self.get_page_schema = get_page_schema_factory(self.get_all_schema)
        self.get_list_schema = get_list_schema_factory(self.get_all_schema)
        self.get_all_response_schema = response_factory(self.get_page_schema, name="GetPage")
        doc = self.get_all.__doc__
        summary = doc.strip().split("\n")[0] if doc else "Get All"
        path = f"/{settings.app_settings.ROUTER_GET_ALL_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._get_all_decorator(),
            methods=["GET"],
            response_model=self.get_all_response_schema,
            summary=summary,
            dependencies=self.get_all_route,
        )
