from tortoise import Model

from fastgenerateapi.pydantic_utils.base_model import BaseModel


class SaveMixin:

    async def set_save_model(self, model: Model, request_data, *args, **kwargs) -> Model:
        """
        添加属性: model.user_id = current_user.id
        """
        return model


