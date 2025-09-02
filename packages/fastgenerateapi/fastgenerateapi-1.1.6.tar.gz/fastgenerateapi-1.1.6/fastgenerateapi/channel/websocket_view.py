from typing import Union

import aioredis

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.controller.ws_controller import WsController
from fastgenerateapi.data_type.data_type import DEPENDENCIES


class WebsocketView(BaseView):
    """
    客户端与服务器之间通信
    """
    websocket_route: Union[bool, DEPENDENCIES] = True
    redis_conn: aioredis.Redis

    def _handler_websocket_settings(self):
        self.ws_summary = WsController(self, self._get_cls_ws_func())
        for ws_router in self.ws_summary.ws_router_data:
            self._add_api_websocket_route(
                f"/{ws_router.path}",
                getattr(self, ws_router.func_name),
                dependencies=ws_router.dependencies,
            )

