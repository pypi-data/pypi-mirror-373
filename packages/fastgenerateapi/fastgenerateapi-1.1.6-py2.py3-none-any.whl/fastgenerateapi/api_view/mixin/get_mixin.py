from tortoise import Model

from fastgenerateapi.pydantic_utils.base_model import BaseModel


class GetMixin:

    async def set_get_model(self, model: Model) -> Model:
        """
        修改查询后的model数据
        """
        return model

