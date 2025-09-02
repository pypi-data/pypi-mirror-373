from typing import Union, Optional, Type, cast, List, Any

from fastapi import Depends, Query
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.controller import SearchController, BaseFilter, FilterController
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.deps import paginator_deps, filter_params_deps
from fastgenerateapi.schemas_factory import get_page_schema_factory, response_factory
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory
from fastgenerateapi.schemas_factory.get_relation_schema_factory import get_relation_schema_factory
from fastgenerateapi.settings.all_settings import settings


class GetRelationView(BaseView):

    path_id_name: str
    relation_id_name: str
    relation_model_class: Optional[Type[Model]]
    get_relation_route: Union[bool, DEPENDENCIES] = True
    get_relation_schema: Optional[Type[BaseModel]] = None
    search_fields: Union[None, list] = None
    filter_fields: Union[None, list] = None
    relation_filter_fields: Union[None, list] = None
    order_by_fields: Union[None, list] = None
    relation_order_by_fields: Union[None, list] = None
    """
    path_id_name: 路径id在模型中对应的字段名
    relation_id_name: 模型中需要修改的字段名
    model_class： 查询数据的模型
    relation_model_class： 多对多数据库模型

    get_relation_route: 获取详情路由开关，可以放依赖函数列表
    get_relation_schema: 返回序列化
        优先级：
            - 传入参数
            - 模型层get_relation_include和get_relation_exclude(同时存在交集)
            - get_one_schemas
    search_fields: search搜索对应字段
        example：("name__contains", str, "name") 类型是str的时候可以省略，没有第三个值时，自动双下划线转单下划线
    filter_fields: 筛选对应字段
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
    relation_filter_fields： 多对多关联表筛选对应字段
    order_by_fields: 排序对应字段
    relation_order_by_fields: 多对多关联表排序对应字段
    """

    async def get_relation(self, pk: str, search: str, filters: dict, relation_filters: dict, *args, **kwargs) -> Union[BaseModel, dict, None]:
        relation_queryset = await self.get_relation_queryset(filters=relation_filters, *args, **kwargs)
        id_list = relation_queryset.filter(eval(f"Q({self.path_id_name}='{pk}')")).values_list(self.relation_id_name, flat=True)

        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)

        return await self.pagination_data(queryset=queryset, id_list=id_list, *args, **kwargs)

    async def get_relation_queryset(self, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理筛选字段；处理排序
        """
        queryset = self.relation_filter_queryset(self.relation_queryset, filters)
        queryset = await self.filter_relation_controller.query(queryset=queryset, values=filters)
        if self.relation_order_by_fields:
            queryset = queryset.order_by(*self.relation_order_by_fields)

        return queryset

    async def get_queryset(self, search: str, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理search搜索；处理筛选字段；处理外键预加载；处理排序
        """
        queryset = self.search_controller.query(queryset=self.queryset, value=search)
        queryset = await self.filter_queryset(queryset, filters)
        queryset = self.filter_controller.query(queryset=queryset, values=filters)
        queryset = queryset.prefetch_related(*self.prefetch_related_fields.keys()).order_by(*self.order_by_fields or [])

        return queryset

    async def relation_filter_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def filter_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def set_get_relation_model(self, model: Model) -> Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    async def pagination_data(
            self,
            queryset: QuerySet,
            id_list,
            paginator,
            fields: List[Union[str, tuple]] = None,
            *args, **kwargs
    ) -> Union[dict, str, None, BaseModel]:

        data_list = []
        if getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
            model_list = await queryset.filter(id__in=id_list).all()
        else:
            current_num = getattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD)
            page_size = getattr(paginator, settings.app_settings.PAGE_SIZE_FIELD)
            if self.relation_order_by_fields:
                id_list = id_list[cast(int, (current_num - 1) * page_size): page_size]
            queryset = queryset.filter(id__in=id_list)
            count = await queryset.count()
            if self.relation_order_by_fields:
                model_list = await queryset
            else:
                queryset = queryset.offset(cast(int, (current_num - 1) * page_size))
                model_list = await queryset.limit(page_size)

        for model in model_list:

            await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields, *args, **kwargs)

            # await self.setattr_model_rpc(self.rpc_class, model, self.rpc_param)
            await self.set_get_relation_model(model)

            if fields:
                data_list.append(await self.getattr_model(model=model, fields=fields))
            else:
                data_list.append(self.get_relation_schema.from_orm(model))

        if getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
            return self.get_relation_list_schema(**{
                settings.app_settings.LIST_RESPONSE_FIELD: data_list,
            })

        return self.get_relation_page_schema(**{
            settings.app_settings.CURRENT_PAGE_FIELD: current_num,
            settings.app_settings.PAGE_SIZE_FIELD: page_size,
            settings.app_settings.TOTAL_SIZE_FIELD: count,
            settings.app_settings.LIST_RESPONSE_FIELD: data_list,
        })

    def _get_relation_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                pk: str,
                request: Request,
                paginator=Depends(paginator_deps()),
                search: str = Query(default="", description="搜索"),
                filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields)),
                relation_filters: dict = Depends(
                    filter_params_deps(model_class=self.relation_model_class, fields=self.relation_filter_fields)),
        ) -> JSONResponse:
            data = await self.get_relation(
                pk=pk,
                paginator=paginator,
                search=search,
                filters=filters,
                relation_filters=relation_filters,
                request=request,
                *args,
                **kwargs
            )
            return self.success(data=data)
        return route

    def _handler_get_relation_settings(self):
        if not self.get_relation_route:
            return
        self.search_controller = SearchController(self.get_base_filter(self.search_fields))
        self.filter_controller = FilterController(self.get_base_filter(self.filter_fields))
        self.filter_relation_controller = FilterController(self.get_base_filter(self.relation_filter_fields))
        self.get_relation_schema = self.get_relation_schema or get_relation_schema_factory(self.model_class)
        self.get_relation_page_schema = get_page_schema_factory(self.get_relation_schema)
        self.get_relation_list_schema = get_list_schema_factory(self.get_relation_schema)
        self.get_relation_response_schema = response_factory(self.get_relation_page_schema, name="GetPage")
        doc = self.get_relation.__doc__
        summary = doc.strip().split("\n")[0] if doc else f"Get {self.model_class.__name__.title()}"
        path = f"/get-{self.relation_id_name.strip('_id')}-by-{self.path_id_name.strip('_id')}/{'{pk}'}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._get_relation_decorator(),
            methods=["GET"],
            response_model=self.get_relation_response_schema,
            summary=summary,
            dependencies=self.get_relation_route,
        )



