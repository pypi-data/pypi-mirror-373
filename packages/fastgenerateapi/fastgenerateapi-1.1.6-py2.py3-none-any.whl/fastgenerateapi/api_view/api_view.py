from fastgenerateapi.api_view.create_view import CreateView
from fastgenerateapi.api_view.delete_view import DeleteView
from fastgenerateapi.api_view.get_all_view import GetAllView
from fastgenerateapi.api_view.get_one_view import GetOneView
from fastgenerateapi.api_view.switch_view import SwitchView
from fastgenerateapi.api_view.update_view import UpdateView


class APIView(CreateView, GetOneView, GetAllView, UpdateView, DeleteView, SwitchView):
    # rpc_class: Type[BaseRPC] = None  # 远程获取数据类型，需要继承BaseRemoteRPC
    # rpc_param: Union[Dict[str, Dict[str, List[Union[str, tuple]]]], Type[RPCParam]] = None  # 远程数据获取参数
    #
    # router_summary: List[Union[str, tuple, BaseRouterSummary]] = None
    """
    # 给函数设置路由以及其他参数
    router_summary = [
        # 内置方法，可添加swagger备注和依赖
        "get_one",
        #("函数名", "默认POST方法", "路由[默认_替换为-]", "[依赖函数]", "swagger备注,默认函数名")
        ("update_avatar", "PATCH", "update-avatar", [依赖函数], "修改头像"),
    ]
    """
    ...





