import inspect
from typing import Union

from fastgenerateapi.settings.all_settings import settings
from pydantic import BaseModel

from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.schemas_factory import response_factory


class BaseRouter(ResponseMixin):
    def __init__(
            self,
            router_class,
            func_name: str,
            func_type=None,
            method: str = "POST",
            prefix: str = None,
            dependencies: DEPENDENCIES = None,
            summary: str = None,
    ):
        self.func_name = func_name
        if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            self.method = method.upper()
        else:
            self.error(msg=f"方法 {func_name} 中 {method} 不符合规范")

        # 此方案放弃
        # if self.method == "GET" and not prefix.endswith("/") and not prefix.endswith("{pk}"):
        #     prefix += "/"
        self.prefix = prefix

        # if function in ["get_one", "get_all", "create", "update", "update_optional", "destroy", "switch"]:
        #     self.is_new = False
        # else:
        #     self.is_new = True
        router_args = router_class.router_args.get(func_name, {}) if router_class.router_args else {}
        if router_args:
            if type(router_args).__name__ == 'ModelMetaclass' and issubclass(router_args, BaseModel):
                router_args = {"response_model": router_args}
            if isinstance(router_args, list):
                router_args = {"dependencies": router_args}
            if isinstance(router_args, str):
                router_args = {"summary": router_args}

        self.dependencies = router_args.get("dependencies") if router_args and router_args.get("dependencies") else []
        self.dependencies += dependencies if dependencies else []

        if router_args and router_args.get("summary"):
            summary = router_args.get("summary")
        if summary is None:
            doc = getattr(router_class, func_name).__doc__
            summary = doc.strip().split("\n")[0] if doc else func_name.lstrip("view_").rstrip("_pk").replace("_",
                                                                                                             " ").title()
        self.summary = summary

        if func_type != inspect._empty and func_type is not None:
            self.response_model = response_factory(func_type)
        elif router_args and router_args.get("response_model"):
            self.response_model = response_factory(router_args.get("response_model"))
        else:
            self.response_model = None


class RouterController:

    def __init__(self, router_class, func_name_return_type_tuple_list):
        self.router_data = []
        for func_name, func_type in func_name_return_type_tuple_list:
            route_info_list = func_name.split("__")
            if route_info_list[-1] in ["pk", "id"]:
                route_info_list[-1] = "{" + route_info_list[-1] + "}"
            route_name = "/".join(route_info_list)
            route_info_list = route_name.split("_")
            method = route_info_list[1].upper()
            middle_list = route_info_list[2:]
            if settings.app_settings.ROUTER_WHETHER_UNDERLINE_TO_STRIKE:
                middle_field = "-".join(middle_list)
            else:
                middle_field = "_".join(middle_list)
            if method == "GET":
                prefix_field = settings.app_settings.RESTFUL_GET_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_GET_ROUTER_ADD_SUFFIX or ""
            elif method == "POST":
                prefix_field = settings.app_settings.RESTFUL_POST_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_POST_ROUTER_ADD_SUFFIX or ""
            elif method == "PUT":
                prefix_field = settings.app_settings.RESTFUL_PUT_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_PUT_ROUTER_ADD_SUFFIX or ""
            elif method == "DELETE":
                prefix_field = settings.app_settings.RESTFUL_DELETE_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_DELETE_ROUTER_ADD_SUFFIX or ""
            else:
                prefix_field = ""
                suffix_field = ""
            if prefix_field:
                prefix_field = prefix_field.strip("/") + "/"
            if suffix_field:
                suffix_field = suffix_field.strip("/") + "/"
            prefix = prefix_field + middle_field + suffix_field

            self.router_data.append(BaseRouter(router_class, func_name, func_type, method, prefix))
            # self.router_data.setdefault(func_name, BaseRouter(router_class, func_name, method, prefix))

    # def get_summary(self, func_name):
    #
    #     return self.router_data.get(func_name).summary
    #
    # def get_dependencies(self, func_name, default: Union[bool, DEPENDENCIES] = None):
    #     dependencies = [] if default is None or isinstance(default, bool) else default
    #
    #     return dependencies | self.router_data.get(func_name).dependencies
