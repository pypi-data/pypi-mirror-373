from fastgenerateapi.settings.all_settings import settings


class WsRouter:

    def __init__(self, router_class, path, func_name):
        router_args = router_class.router_args.get(func_name, {}) if router_class.router_args else {}
        if router_args and isinstance(router_args, list):
            router_args = {"dependencies": router_args}

        self.dependencies = router_args.get("dependencies") if router_args and router_args.get("dependencies") else []
        self.path = path
        self.func_name = func_name

        name = None
        if router_args and router_args.get("name"):
            name = router_args.get("name")
        if name is None:
            doc = getattr(router_class, func_name).__doc__
            if doc:
                name = doc.strip().split("\n")[0]
        self.name = name or None


class WsController:

    def __init__(self, router_class, func_name_list):
        self.ws_router_data = []
        for func_name in func_name_list:
            route_info_list = func_name.split("__")
            if route_info_list[-1] in ["pk", "id"]:
                route_info_list[-1] = "{" + route_info_list[-1] + "}"
            route_name = "/".join(route_info_list)
            route_info_list = route_name.split("_")
            # method = route_info_list[0]  # ws
            middle_list = route_info_list[1:]
            if settings.app_settings.ROUTER_WHETHER_UNDERLINE_TO_STRIKE:
                path = "-".join(middle_list)
            else:
                path = "_".join(middle_list)

            self.ws_router_data.append(WsRouter(router_class, path, func_name))


