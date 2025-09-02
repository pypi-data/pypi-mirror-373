from typing import Optional, Type, Union, Any

from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.save_mixin import SaveMixin
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.schemas_factory import get_one_schema_factory, create_schema_factory, response_factory
from fastgenerateapi.settings.all_settings import settings


class CreateView(BaseView, SaveMixin):

    create_schema: Optional[Type[BaseModel]] = None
    create_route: Union[bool, DEPENDENCIES] = True
    """
    create_schema: 创建请求模型;
        优先级：  
            - create_schema：参数传入
            - create_schema_factory：数据库模型自动生成
                - 优选模型层[include, exclude, create_include, create_exclude](同时存在交集)
                - 无include和exclude默认模型层所有字段
    create_route: 创建路由开关，可以放依赖函数列表
    """

    @atomic()
    async def create(self, request_data, *args, **kwargs):
        try:
            model = await self.set_create_fields(request_data=request_data, *args, **kwargs)
        except ValueError as e:
            error_field = str(e).split(" ")[0]
            if getattr(request_data, error_field):
                return self.error(msg=f"{self.get_field_description(self.model_class, error_field)}格式不正确")
            return self.error(msg=f"{self.get_field_description(self.model_class, error_field)}不能为空")

        model = await self.set_save_model(model=model, request_data=request_data, *args, **kwargs)

        model = await self.set_create_model(model=model, request_data=request_data, *args, **kwargs)

        await self.check_unique_field(model, model_class=self.model_class)

        await model.save()

        model = await self.model_class.filter(id=model.id).prefetch_related(
            *self.prefetch_related_fields.keys()).first()

        await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields)

        # await self.setattr_model_rpc(self.rpc_class, model, self.rpc_param)

        return self.get_one_schema.from_orm(model)

    async def set_create_fields(self, request_data, *args, **kwargs):
        """
        添加属性: request_data.user_id = request.user.id
        """

        return self.model_class(**request_data.dict(exclude_unset=True))

    async def set_create_model(self, model: Model, request_data, *args, **kwargs) -> Model:
        """
        添加属性: model.user_id = request.user.id
        """

        return model

    def _create_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request_data: self.create_schema,  # type: ignore
                request: Request,
        ) -> JSONResponse:
            data = await self.create(
                request_data=request_data,
                request=request,
                *args,
                **kwargs
            )
            return self.success(data=data)
        return route

    def _handler_create_settings(self):
        if not self.create_route:
            return
        self.create_schema = self.create_schema or create_schema_factory(self.model_class)
        if not hasattr(self, "get_one_schema"):
            self.get_one_schema = get_one_schema_factory(model_class=self.model_class)
        if not hasattr(self, "get_one_response_schema"):
            self.get_one_response_schema = response_factory(self.get_one_schema, name="GetOne")
        doc = self.create.__doc__
        summary = doc.strip().split("\n")[0] if doc else f"Create"
        path = f"/{settings.app_settings.ROUTER_CREATE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._create_decorator(),
            methods=["POST"],
            response_model=self.get_one_response_schema,  # type: ignore
            summary=summary,
            dependencies=self.create_route,
        )









