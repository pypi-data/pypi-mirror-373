import time
import uuid
from copy import copy
from typing import Optional, Type, List, Union, Sequence, Dict
from urllib.parse import parse_qs

from fastapi import params
from tortoise.queryset import QuerySet

from pydantic import create_model, BaseModel
from starlette.requests import Request
from tortoise import Model

from fastgenerateapi.api_view.mixin.base_mixin import BaseMixin
from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin
from fastgenerateapi.api_view.mixin.tool_mixin import ToolMixin
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND


class BaseView(BaseMixin, ResponseMixin, ToolMixin, DBModelMixin):

    prefix: Optional[str] = None  # 路由追加后缀
    model_class: Optional[Type[Model]] = None  # 数据库模型
    prefetch_related_fields: Union[None, dict] = None
    schema: Optional[Type[BaseModel]] = None  # 返回序列化
    dependencies: Optional[Sequence[params.Depends]] = None
    tags: Optional[List[str]] = None  # swagger标签
    router_args: Dict[str, any] = None

    """
    # 增加外键字段显示
    prefetch_related_fields = {
          "avatar": None,           # 外键内容对应字典的形式
          "avatar": ["id", ("url", "avatar_url")]   # 增加 avatar_id,avatar_url2个字段
    }

    # router_args: List[Union[str, tuple, BaseRouterSummary]] = None
    # 给函数设置路由以及其他参数
    # key为方法名，例如："get_one", "view_get_data"
    router_args = {
        "get_one": {
            "response_model": CommonResponse;
            "summary": "备注",
            "dependencies": ["依赖函数"],
        }
        // 或者 "get_one": CommonResponse,
        // 或者 "get_one": "备注",
        // 或者 "get_one": ["依赖函数"],
    }
    """

    @property
    def queryset(self) -> QuerySet:
        if not self.model_class:
            return self.error(msg="model_class not allow None")

        return self.get_active_queryset(self.model_class)

    def get_active_queryset(self, model_class: Union[Type[Model], QuerySet, None] = None) -> QuerySet:
        if not model_class:
            if not self.model_class:
                return self.error(msg="model_class not allow None")
            model_class = self.model_class
        delete_filter_field = settings.app_settings.WHETHER_DELETE_FIELD
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            delete_filter_field = f"{settings.app_settings.WHETHER_DELETE_FIELD}__isnull"
        queryset = model_class.filter(**{
            delete_filter_field: True
        })

        return queryset

    @property
    def relation_queryset(self) -> QuerySet:
        if not self.relation_model_class:
            return self.error(msg="relation_model_class not allow None")
        return self.get_active_queryset(self.relation_model_class)

    async def get_object(self, pk):
        model = await self.queryset.filter(pk=pk).prefetch_related(
            *self.prefetch_related_fields.keys()).first()
        if model:
            return model
        else:
            raise NOT_FOUND

    def _delete_value(self):
        result = False
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            result = int(time.time() * 1000)
        return result

    async def delete_queryset(self, queryset: QuerySet):
        """
        考虑到不一定会集成已有的模型，删除根据是否存在字段来判断
        :param queryset:
        :return:
        """
        if settings.app_settings.WHETHER_DELETE_FIELD in queryset.fields:
            await queryset.update(**{
                settings.app_settings.WHETHER_DELETE_FIELD: self._delete_value()
            })
        else:
            await queryset.delete()

    @staticmethod
    async def setattr_model(model: Model, prefetch_related_fields, *args, **kwargs) -> Model:
        for key, value_list in prefetch_related_fields.items():
            if value_list is None:
                continue
            if isinstance(value_list, str):
                value_list = [value_list]
            key_list = key.split("__")
            attr_model = copy(model)
            for attr_key in key_list:
                attr_model = getattr(attr_model, attr_key, None)

            if attr_model:
                for value in value_list:
                    if type(value) == str:
                        setattr(model, key + "_" + value, getattr(attr_model, value, None) if attr_model else None)
                    elif type(value) == tuple and len(value) == 2:
                        setattr(model, value[1], getattr(attr_model, value[0], None) if attr_model else None)
        return model

    @staticmethod
    async def getattr_model(model: Model, fields: List[Union[str, tuple]]) -> BaseModel:
        model_dict = {}
        model_fields = {}
        for field in fields:
            if type(field) == str:
                key_list = field.split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field] = attr_model
                model_fields[field] = (type(attr_model), ...)
            if type(field) == tuple and len(field) == 2:
                key_list = field[0].split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field[1]] = attr_model
                model_fields[field[1]] = (type(attr_model), ...)
        schema = create_model(
            f"{Model.__name__}{uuid.uuid4()}",
            **model_fields
        )
        return schema.model_validate(model_dict)

    async def check_unique_field(
            self,
            request_data: Union[BaseModel, Model],  # 创建或修改的参数数据
            model_class: Type[Model],       # 数据库模型
            model: Union[Model, None] = None
    ):
        check_unique_fields = self._get_unique_fields(model_class) + self._get_foreign_key_fields(model_class)
        check_unique_together_fields = self._get_unique_together_fields(model_class)
        for unique_field in check_unique_fields:
            if hasattr(request_data, unique_field):
                if model and getattr(request_data, unique_field) == getattr(model, unique_field):
                    continue
                if await model_class.filter(**{unique_field: getattr(request_data, unique_field)}).first():
                    self.fail(message=f"{self.get_field_description(model_class, unique_field)}已存在相同值：{getattr(request_data, unique_field)}")
        for unique_together_fields in check_unique_together_fields:
            filter_fields = {}
            is_equal = True
            description_fields = []
            for unique_together_field in unique_together_fields:
                if model:
                    if hasattr(request_data, unique_together_field):
                        filter_fields[unique_together_field] = getattr(request_data, unique_together_field)
                        if getattr(request_data, unique_together_field, None) != getattr(model, unique_together_field):
                            is_equal = False
                            description_fields.append(unique_together_field)
                    else:
                        filter_fields[unique_together_field] = getattr(model, unique_together_field)
                else:
                    if hasattr(request_data, unique_together_field):
                        is_equal = False
                        description_fields.append(unique_together_field)
                        filter_fields[unique_together_field] = getattr(request_data, unique_together_field)
            if is_equal:
                continue

            if await model_class.filter(**filter_fields).first():
                self.fail(
                    message=f"{self.get_field_description(model_class, description_fields)}已存在相同值：{[filter_fields.get(field) for field in description_fields]}"
                )

    # @staticmethod
    # async def setattr_model_rpc(
    #         rpc_class,
    #         model: Model,
    #         rpc_param: Union[Dict[str, Dict[str, List[Union[str, tuple]]]], Type[RPCParam]],
    #         *args, **kwargs
    # ) -> Model:
    #     if rpc_class is None or not model or not rpc_param:
    #         return model
    #     if not isinstance(rpc_param, RPCParam):
    #         rpc_param = RPCParam(rpc_param, model)
    #     rpc_obj = rpc_class(**rpc_param.request_param)
    #     await rpc_obj.get_data()
    #     for base_rpc_param in rpc_param.data:
    #         setattr(
    #             model,
    #             base_rpc_param.response_field_alias_name,
    #             rpc_obj.filter(base_rpc_param.model_field_value).get(base_rpc_param.response_field_name))
    #     return model

    @staticmethod
    async def get_params(request: Request) -> dict:
        result = {}
        data = parse_qs(str(request.query_params), keep_blank_values=False)
        for key, val in data.items():
            result[key] = val[0]
        return result



