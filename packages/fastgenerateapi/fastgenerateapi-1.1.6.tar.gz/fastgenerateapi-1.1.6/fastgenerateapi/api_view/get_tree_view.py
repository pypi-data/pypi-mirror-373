from typing import Union, Optional, Type, cast, List, Any, Callable, Coroutine

from fastapi import Depends, Query
from fastapi.types import DecoratedCallable
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from fastgenerateapi.cache.cache_decorator import tree_cache_decorator
from fastgenerateapi.cache.key_builder import generate_key_builder
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory

from fastgenerateapi.utils.exception import NOT_FOUND
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.get_mixin import GetMixin
from fastgenerateapi.controller import SearchController, BaseFilter, FilterController
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.deps import paginator_deps, filter_params_deps
from fastgenerateapi.deps.tree_params_deps import tree_params_deps
from fastgenerateapi.schemas_factory import get_one_schema_factory, response_factory
from fastgenerateapi.schemas_factory.get_tree_schema_factory import get_tree_schema_factory
from fastgenerateapi.settings.all_settings import settings


class GetTreeView(BaseView):

    get_tree_route: Union[bool, DEPENDENCIES] = True
    get_tree_schema: Optional[Type[BaseModel]] = None
    search_fields: Union[None, list] = None
    filter_fields: Union[None, list] = None
    order_by_fields: Union[None, list] = None
    """
    get_tree_route: 获取树状数据路由开关，可以放依赖函数列表
    get_tree_schema: 返回序列化
        优先级：  
            - 传入参数
            - 模型层get_tree_include和get_tree_exclude(同时存在交集)
            - include和exclude(同时存在交集)
    search_fields: search搜索对应字段 
        example：("name__contains", str, "name") 类型是str的时候可以省略，没有第三个值时，自动双下划线转单下划线
    filter_fields: 筛选对应字段
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
    order_by_fields: 排序对应字段
    """

    async def get_tree(
            self,
            node_id: Optional[str],
            search: str,
            filters: dict,
            request, *args, **kwargs
    ) -> Union[BaseModel, dict, None]:
        if settings.app_settings.METHOD_TREE_CHOICE.upper() == "MAP":
            data_list = await self.map_method(
                node_id=node_id, search=search, filters=filters, request=request, *args, **kwargs)
        else:
            data_list = await self.recursion_method(
                node_id=node_id, search=search, filters=filters, request=request, *args, **kwargs)

        return self.get_tree_data_schema(**{settings.app_settings.LIST_RESPONSE_FIELD: data_list})

    async def map_method(
            self,
            node_id: Optional[str],
            search: str,
            filters: dict,
            request, *args, **kwargs
    ) -> list:
        data_map = {}
        parent_id_field = settings.app_settings.DEFAULT_TREE_PARENT_FIELD + '_id'
        children_field = settings.app_settings.DEFAULT_TREE_CHILDREN_FIELD
        queryset = await self.get_tree_queryset(self.queryset, search, filters)
        for node_data in await queryset:
            node_dict = self.get_tree_schema.from_orm(node_data).dict(exclude_unset=True)
            data_map[node_data.id] = node_dict

        data_list = []
        for index, data_dict in data_map.items():
            parent_id = data_dict.get(parent_id_field)
            parent_dict = data_map.get(parent_id)
            if node_id == parent_id:
                data_list.append(data_dict)
            elif parent_id and parent_dict:
                parent_dict.setdefault(children_field, []).append(data_dict)

        return data_list

    async def recursion_method(
            self,
            node_id: Optional[str],
            search: str,
            filters: dict,
            request, *args, **kwargs
    ) -> list:
        if node_id:
            queryset = self.queryset.filter(pk=node_id).prefetch_related(settings.app_settings.DEFAULT_TREE_PARENT_FIELD)
            queryset = await self.get_tree_queryset(queryset, search, filters)
            top_node = await queryset.first()
            if not top_node:
                raise NOT_FOUND
            top_nodes = [top_node]
        else:
            queryset = self.queryset.filter(
                eval(f"Q({settings.app_settings.DEFAULT_TREE_PARENT_FIELD + '_id'}={None})")
            ).prefetch_related(settings.app_settings.DEFAULT_TREE_PARENT_FIELD)

            queryset = await self.get_tree_queryset(queryset, search, filters)
            top_nodes = await queryset

        data_list = [await self.get_tree_recursion(node, search, filters) for node in top_nodes]

        return data_list

    async def get_tree_queryset(self, queryset: QuerySet, search: str, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理search搜索；处理筛选字段；处理外键预加载；处理排序
        """
        # queryset = self.search_controller.query(queryset=queryset, value=search)
        # queryset = await self.filter_tree_queryset(queryset, filters)
        # queryset = self.filter_controller.query(queryset=queryset, values=filters)
        queryset = queryset.prefetch_related(*self.prefetch_related_fields.keys())
        if self.order_by_fields:
            queryset = queryset.order_by(*self.order_by_fields)

        return queryset

    async def get_tree_recursion(self, node, search: str, filters: dict,):
        data = self.get_tree_schema.from_orm(node)
        pk = getattr(data, self._get_pk_field(self.model_class))
        children_queryset = self.queryset.filter(eval(f"Q({settings.app_settings.DEFAULT_TREE_PARENT_FIELD + '_id'}={pk})"))
        children_queryset = await self.get_tree_queryset(children_queryset, search, filters)
        children_objs = await children_queryset
        if not children_objs:
            return data
        children_list = []
        for children_obj in children_objs:
            children_list.append(await self.get_tree_recursion(children_obj, search, filters))
        setattr(data, settings.app_settings.DEFAULT_TREE_CHILDREN_FIELD, children_list)
        return data

    async def set_get_tree_model(self, model: Model) -> Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    def _get_tree_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        @tree_cache_decorator(cache(expire=settings.app_settings.CACHE_TREE_SECONDS, coder=JsonCoder, key_builder=generate_key_builder))
        async def route(
                request: Request,
                search: str = Query(default="", description="搜索"),
                node_id: Optional[str] = Depends(tree_params_deps()),
                filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields)),
        ) -> JSONResponse:
            data = await self.get_tree(
                search=search,
                node_id=node_id,
                filters=filters,
                request=request,
                *args,
                **kwargs
            )
            return self.success(data=data)
        return route

    def _handler_get_tree_settings(self):
        if not self.get_tree_route:
            return
        self.search_controller = SearchController(self.get_base_filter(self.search_fields))
        self.filter_controller = FilterController(self.get_base_filter(self.filter_fields))
        self.get_tree_schema = self.get_tree_schema or get_tree_schema_factory(self.model_class)
        self.get_tree_data_schema = get_list_schema_factory(self.get_tree_schema)
        self.get_tree_response_schema = response_factory(self.get_tree_data_schema, name="GetTree")
        doc = self.get_tree.__doc__
        summary = doc.strip().split("\n")[0] if self.get_tree.__doc__ else "Get Tree"
        path = f"/{settings.app_settings.ROUTER_GET_TREE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._get_tree_decorator(),
            methods=["GET"],
            response_model=self.get_tree_response_schema,
            summary=summary,
            dependencies=self.get_tree_route,
        )

    # async def filter_tree_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
    #     """
    #     处理filters
    #         example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
    #     """
    #     return queryset

