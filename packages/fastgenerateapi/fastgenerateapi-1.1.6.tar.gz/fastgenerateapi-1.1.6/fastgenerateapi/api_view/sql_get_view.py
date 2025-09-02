# from typing import Union, Optional, Type, cast, List, Any
#
# from fastapi import Depends, Query
# from fastapi.types import DecoratedCallable
# from starlette.requests import Request
# from starlette.responses import JSONResponse
# from tortoise import run_async, Tortoise
# from tortoise.expressions import Q
#
# from fastgenerateapi.api_view.base_view import BaseView
# from fastgenerateapi.api_view.mixin.get_mixin import GetMixin
# from fastgenerateapi.data_type.data_type import DEPENDENCIES
# from fastgenerateapi.deps import paginator_deps, filter_params_deps
# from fastgenerateapi.pydantic_utils.base_model import BaseModel
# from fastgenerateapi.schemas_factory import get_page_schema_factory, response_factory
# from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory
# from fastgenerateapi.schemas_factory.sql_get_all_schema_factory import sql_get_all_schema_factory
# from fastgenerateapi.settings.register_settings import settings
#
#
# class SQLGetAllView(BaseView, GetMixin):
#
#     sql_get_all_route: Union[bool, DEPENDENCIES] = True
#     include_fields = []
#     exclude_fields = []
#     table_name: Optional[str] = None
#     connection_name: Optional[str] = "default"
#     # search_fields: Union[None, list] = None
#     # filter_fields: Union[None, list] = None
#     """
#     get_all_route: 获取详情路由开关，可以放依赖函数列表
#     get_all_schema: 返回序列化
#         优先级：
#             - 传入参数
#             - 模型层get_all_include和get_all_exclude(同时存在交集)
#             - get_one_schemas
#     """
#
#     # async def sql_get_all(self, search: str, filters: dict, paginator, *args, **kwargs) -> Union[BaseModel, dict, None]:
#     async def sql_get_all(self, paginator, *args, **kwargs) -> Union[BaseModel, dict, None]:
#         sql, count_sql = await self.handler_sql(paginator)
#
#         data = await self.conn.execute_query_dict(sql)
#
#         data = await self.handler_paginator(data, paginator, count_sql)
#         return data
#
#     async def handler_sql(self, paginator):
#         delete_field = settings.app_settings.WHETHER_DELETE_FIELD
#         active_value = 1 if settings.app_settings.ACTIVE_DEFAULT_VALUE else 0
#         where_str = f"WHERE {delete_field} = {active_value}"
#         if getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
#             current_num = getattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD)
#             page_size = getattr(paginator, settings.app_settings.PAGE_SIZE_FIELD)
#             sql = f"SELECT {','.join(self.fields)} {where_str} FROM {self.table_name} OFFSET {cast(int, (current_num - 1) * page_size)} LIMIT {page_size}"
#             count_sql = f"SELECT COUNT(*) {where_str} FROM {self.table_name}"
#         else:
#             sql = f"SELECT {','.join(self.fields)} {where_str} FROM {self.table_name}"
#             count_sql = None
#         return sql, count_sql
#
#     async def handler_paginator(self, data, paginator, count_sql: Optional[str] = None) -> Union[dict, str, None]:
#         if not data:
#             return {}
#
#         if not paginator or getattr(paginator, settings.app_settings.DETERMINE_WHETHER_PAGE_FIELD) == settings.app_settings.DETERMINE_PAGE_BOOL_VALUE:
#             return self.sql_get_list_schema(**{
#                 settings.app_settings.LIST_RESPONSE_FIELD: data,
#             })
#         current_num = getattr(paginator, settings.app_settings.CURRENT_PAGE_FIELD)
#         page_size = getattr(paginator, settings.app_settings.PAGE_SIZE_FIELD)
#         count = (await self.conn.execute_query_dict(count_sql))[0].get("COUNT(*)", 0)
#
#         return self.sql_get_page_schema(**{
#             settings.app_settings.CURRENT_PAGE_FIELD: current_num,
#             settings.app_settings.PAGE_SIZE_FIELD: page_size,
#             settings.app_settings.TOTAL_SIZE_FIELD: count,
#             settings.app_settings.LIST_RESPONSE_FIELD: data,
#         })
#
#     @property
#     def conn(self):
#         try:
#             conn = Tortoise.get_connection(self.connection_name)
#         except Exception:
#             Tortoise.init()
#             conn = Tortoise.get_connection(self.connection_name)
#         return conn
#
#     def _sql_get_all_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
#         async def route(
#                 request: Request,
#                 paginator=Depends(paginator_deps()),
#                 # search: str = Query(default="", description="搜索"),
#                 # filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields)),
#         ) -> JSONResponse:
#             data = await self.sql_get_all(
#                 paginator=paginator,
#                 # search=search,
#                 # filters=filters,
#                 request=request,
#                 *args,
#                 **kwargs
#             )
#
#             return self.success(data=data)
#         return route
#
#     def _handler_sql_get_all_settings(self):
#         if not self.sql_get_all_route:
#             return
#
#         # self.search_controller = SearchController(get_base_filter_list(self.search_fields))
#         # self.filter_controller = FilterController(get_base_filter_list(self.filter_fields))
#         field_info = run_async(self.conn.execute_query_dict(f"SELECT * FROM information_schema.columns WHERE TABLE_NAME = {self.table_name}"))
#         self.sql_get_schema = sql_get_all_schema_factory(field_info, self.include_fields, self.exclude_fields)
#         self.sql_get_page_schema = get_page_schema_factory(self.sql_get_schema)
#         self.sql_get_list_schema = get_list_schema_factory(self.sql_get_schema)
#         self.sql_get_all_response_schema = response_factory(self.sql_get_page_schema, name="SQLGetPage")
#         doc = self.sql_get_all.__doc__
#         summary = doc.strip().split("\n")[0] if doc else "Get All"
#         path = f"/{settings.app_settings.ROUTER_GET_ALL_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
#         self._add_api_route(
#             path=path,
#             endpoint=self._sql_get_all_decorator(),
#             methods=["GET"],
#             response_model=self.sql_get_all_response_schema,
#             summary=summary,
#             dependencies=self.sql_get_all_route,
#         )
#
#
#
#
#
#    存在问题，生成shemas时，未初始化tortoise
#
#
#
#
#
#
