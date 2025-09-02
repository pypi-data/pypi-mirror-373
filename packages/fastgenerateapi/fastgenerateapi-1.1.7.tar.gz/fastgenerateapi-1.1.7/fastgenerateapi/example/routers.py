from fastapi import APIRouter
from starlette.routing import WebSocketRoute

from fastgenerateapi.example.views import ChatView, ChatGroupView
from fastgenerateapi.example.views import StaffView, CompanyView

router = APIRouter()

router.include_router(StaffView())
router.include_router(CompanyView())

router.include_router(ChatView())
router.routes.append(WebSocketRoute("/group", ChatGroupView, name="群聊测试"))


