import inspect
from abc import ABC
from typing import List, Callable, Any, Union, Optional, Generic, Type

from fastapi import APIRouter
from fastapi.types import DecoratedCallable
from fastgenerateapi.utils.exception import NOT_FOUND

from fastgenerateapi.controller.filter_controller import BaseFilter
from fastgenerateapi.controller import RouterController
from fastgenerateapi.controller.ws_controller import WsController

from fastgenerateapi.settings.all_settings import settings
from starlette.exceptions import HTTPException

from fastgenerateapi.data_type.data_type import DEPENDENCIES, T, PYDANTIC_SCHEMA


class BaseMixin(Generic[T], APIRouter, ABC):

    def __init__(self, **kwargs):
        self.prefetch_related_fields: dict = self.prefetch_related_fields or {}
        try:
            prefix = self.prefix or self.get_model_prefix_name(self.model_class)
            prefix = "/" + prefix.strip("/")
        except Exception:
            prefix = ""
        try:
            tags = self.tags or [self.get_model_description(self.model_class) or prefix.strip("/").capitalize()]
        except Exception:
            tags = None
        super().__init__(prefix=prefix, tags=tags, dependencies=self.dependencies, **kwargs)

        self.router_summary = RouterController(self, self._get_cls_api_func())
        for router in self.router_summary.router_data:
            self._add_api_route(
                f"/{router.prefix}",
                getattr(self, router.func_name),
                methods=[router.method],
                response_model=router.response_model,
                summary=router.summary,
                dependencies=router.dependencies,
                error_responses=[NOT_FOUND],
            )

        if self.model_class:
            for route_field in self._get_routes(is_controller_field=True):
                route_field_func = f"_handler_{route_field.rsplit('_', 1)[0]}_settings"
                if hasattr(self, route_field) and getattr(self, route_field) and hasattr(self, route_field_func):
                    getattr(self, route_field_func)()
        # if self.table_name:
        #     if hasattr(self, "_handler_sql_get_all_settings"):
        #         getattr(self, "_handler_sql_get_all_settings")()

    def get_base_filter(self, fields: list, schema: Optional[PYDANTIC_SCHEMA] = None) -> list:
        bast_filter_list = []
        if fields:
            bast_filter_list += [BaseFilter(field) if not isinstance(field, BaseFilter) else field for field in fields]
        if schema:
            bast_filter_list += [BaseFilter((field, model_field.alias)) for field, model_field in schema.__fields__.items()]
        return bast_filter_list

    @staticmethod
    def _get_routes(is_controller_field: bool = False) -> List[str]:
        if is_controller_field:
            return ["get_one_route", "get_all_route", "get_tree_route", "create_route",
                    "update_route", "update_relation_route", "delete_route", "delete_tree_route", "switch_route_fields",
                    "websocket_route"]
        return ["get_one", "get_all", "get_tree", "create", "update", "update_relation", "destroy", "destroy_tree",
                "destroy_filter", "switch"]

    @classmethod
    def _get_cls_api_func(cls):
        func_list = inspect.getmembers(cls, inspect.isfunction)

        return [(func[0], inspect.signature(func[1]).return_annotation) for func in func_list if
                func[0].startswith("view_")]

    @classmethod
    def _get_cls_ws_func(cls):
        func_list = inspect.getmembers(cls, inspect.isfunction)
        return [func[0] for func in func_list if func[0].startswith("ws_")]

    def _add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            dependencies: Union[bool, DEPENDENCIES],
            error_responses: Optional[List[HTTPException]] = None,
            **kwargs: Any,
    ) -> None:
        dependencies = [] if isinstance(dependencies, bool) else dependencies
        responses: Any = (
            {err.status_code: {"detail": err.detail} for err in error_responses}
            if error_responses
            else None
        )

        self.add_api_route(
            path, endpoint, dependencies=dependencies, responses=responses, **kwargs
        )

    def _add_api_websocket_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            name: Optional[str] = None,
            *,
            dependencies: Union[bool, DEPENDENCIES],
            # dependencies: Optional[Sequence[params.Depends]] = None,
            **kwargs: Any,
    ) -> None:
        dependencies = [] if isinstance(dependencies, bool) else dependencies

        self.add_api_websocket_route(
            path, endpoint, name=name, dependencies=dependencies
        )

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self._remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self._remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self._remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self._remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def patch(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self._remove_api_route(path, ["PATCH"])
        return super().put(path, *args, **kwargs)

    def delete(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self._remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def _remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                    route.path == f"{self.prefix}{path}"  # type: ignore
                    and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)
