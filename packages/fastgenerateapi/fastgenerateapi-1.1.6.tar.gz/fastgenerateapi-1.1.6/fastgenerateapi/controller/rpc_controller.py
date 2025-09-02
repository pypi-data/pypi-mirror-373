

# 待优化，暂时未应用
from typing import Union, Dict, List

from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin


class BaseRPC:
    def __init__(self):
        raise NotImplementedError

    async def get_data(self):
        raise NotImplementedError

    async def filter(self):
        raise NotImplementedError


class BaseRPCParam:

    def __init__(self, request_param_key, model_field, model_field_value, response_field_name, response_field_alias_name):
        self.request_param_key = request_param_key
        self.model_field = model_field
        self.model_field_value = model_field_value
        self.response_field_name = response_field_name
        self.response_field_alias_name = response_field_alias_name


class RPCController(ResponseMixin):
    def __init__(self, data: Union[Dict[str, Dict[str, List[Union[str, tuple]]]], None], model):
        self.data = []
        if data is not None:
            for request_param_key, data_value in data:
                for model_field, request_param_value_list in data_value:
                    model_field_value = getattr(model, model_field, None)
                    for response_param_value in request_param_value_list:
                        if type(response_param_value) == str:
                            response_field_name = response_param_value
                            response_field_alias_name = model_field.rstrip("_id") + "_" + response_param_value
                        elif type(response_param_value) == tuple and len(response_param_value) > 1:
                            response_field_name = response_param_value[0]
                            response_field_alias_name = response_param_value[1]
                        else:
                            self.error(msg=f"{response_param_value} is error")
                        self.data.append(BaseRPCParam(request_param_key, model_field, model_field_value, response_field_name, response_field_alias_name))

    @property
    def request_param(self):
        # {"user_id_list": ["creator_id", ...], }
        data = {}
        for base_param in self.data:
            data.setdefault(base_param.request_param_key, []).extend(base_param.model_field_value)
        return data
