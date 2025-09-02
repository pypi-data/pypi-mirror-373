#           dP       oo   dP oo
#           88            88
#  .d8888b. 88d888b. dP   88 dP .d8888b. 88d888b. .d8888b.
#  Y8ooooo. 88'  `88 88   88 88 88'  `88 88'  `88 88'  `88
#        88 88    88 88   88 88 88.  .88 88    88 88.  .88
#  `88888P' dP    dP dP   dP dP `88888P8 dP    dP `8888P88
#                                                      .88
#                                                  d8888P


from fastgenerateapi.api_view.api_view import APIView, CreateView, GetOneView, GetAllView, UpdateView, DeleteView, \
    SwitchView
from fastgenerateapi.api_view.get_tree_view import GetTreeView
from fastgenerateapi.api_view.delete_tree_view import DeleteTreeView
from fastgenerateapi.api_view.delete_filter_view import DeleteFilterView
from fastgenerateapi.api_view.base_view import BaseView

# 多对多关联 >> 查和改
from fastgenerateapi.api_view.get_relation_view import GetRelationView
from fastgenerateapi.api_view.update_relation_view import UpdateRelationView

# Websocket 视图以及分组 发送数据
from fastgenerateapi.channel.websocket_view import WebsocketView
from fastgenerateapi.channel.consumer import Consumer

# 模型相关类
from fastgenerateapi.pydantic_utils.base_model import model_config, BaseModel, IdList

