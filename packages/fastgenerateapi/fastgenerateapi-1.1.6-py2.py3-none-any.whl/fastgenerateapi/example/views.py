from fastapi import Depends
from fastapi_cache.decorator import cache
from starlette.websockets import WebSocket

from fastgenerateapi import APIView, DeleteTreeView, GetTreeView, WebsocketView, Consumer
from fastgenerateapi.deps import paginator_deps
# from middlewares.jwt_middleware.schemas import UserObject
from fastgenerateapi.example.models import StaffInfo, CompanyInfo
from fastgenerateapi.example.schemas import CompanyInfoRead, CompanyInfoCreate, ListTestSchema, StaffReadSchema


class CompanyView(APIView, DeleteTreeView, GetTreeView):
    model_class = CompanyInfo
    # schema = CompanyInfoRead
    # create_schema = CompanyInfoCreate

    @cache()
    async def view_get_list(self, paginator=Depends(paginator_deps())):

        return await self.pagination_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)


class StaffView(APIView):

    def __init__(self):
        self.model_class = StaffInfo
        self.order_by_fields = ["-created_at"]
        self.prefetch_related_fields = {"company": ["name"]}
        # self.router_args = {
        #     # "view_get_staff_list": ListTestSchema
        #     "view_get_staff_list": TestSchema
        # }
        self.get_all_schema = StaffReadSchema
        # self.dependencies = [Depends(ADG.authenticate_user_deps), ]
        super().__init__()

    # async def get_one(self, pk: str, *args, **kwargs) -> Union[BaseModel, dict, None]:
    #     print(datetime.datetime.now())
    #     data = await super().get_one(pk=pk, *args, **kwargs)
    #     result = create_staff.delay()
    #     print(result.id)
    #     print(datetime.datetime.now())
    #     return data

    # async def view_get_staff_list(self, name: Optional[str] = None):
    #     conn = Tortoise.get_connection("default")
    #     # conn = Tortoise.get_connection("local")
    #     val = await conn.execute_query_dict("SELECT * FROM information_schema.columns WHERE TABLE_NAME = 'staffinfo'")
    #     # val = await conn.execute_query_dict("SELECT * FROM staffinfo")
    #     print(val)
    #     return self.success(data={"data_list": val})

    @cache()
    async def view_get_staff_list(
            self,
            paginator=Depends(paginator_deps()),
            # current_user: UserObject = Depends(ADG.authenticate_user_deps),
    ) -> ListTestSchema:
        data = await self.pagination_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)
        return self.success(data=data)


# class StaffView(SQLGetAllView):
#     table_name = "staffinfo"


class ChatView(WebsocketView):
    """
    客户端与服务端场链接测试
    """
    # redis_conn = default_redis
    tags = ["ws测试"]

    async def ws_wschat_pk(self, websocket: WebSocket, pk: str):
        """
        测试
        """
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()
                await websocket.send_text(f"接受到的消息是: {data}")
            except Exception:
                print(1)


class ChatGroupView(Consumer):
    """
    群聊测试
    """
    # redis_conn = default_redis
    ...






