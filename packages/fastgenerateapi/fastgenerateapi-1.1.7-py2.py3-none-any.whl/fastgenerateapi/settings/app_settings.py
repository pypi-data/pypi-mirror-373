from typing import Optional

from pydantic import Field
from fastgenerateapi.pydantic_utils.base_settings import BaseSettings


class AppSettings(BaseSettings):
    # 字段配置 老版本(pydantic.utils.to_lower_camel)
    ALIAS_GENERATOR: Optional[str] = Field(default="pydantic.alias_generators.to_snake", description="序列化参数命名方法路径")

    # 分页对应字段以及配置默认值
    CURRENT_PAGE_FIELD: Optional[str] = Field(default="page", description="当前页字段")
    PAGE_SIZE_FIELD: Optional[str] = Field(default="page_size", description="每页数量字段")
    TOTAL_SIZE_FIELD: Optional[str] = Field(default="total", description="统计数量字段")
    DETERMINE_WHETHER_PAGE_FIELD: Optional[str] = Field(default="no_page", description="判断是否分页字段")
    DETERMINE_PAGE_BOOL_VALUE: Optional[bool] = Field(default=True, description="分页对应的布尔值")
    DEFAULT_WHETHER_PAGE: Optional[bool] = Field(default=False, description="默认是否分页")
    DEFAULT_PAGE_SIZE: Optional[int] = Field(default=10, description="默认每页数量")
    DEFAULT_MAX_PAGE_SIZE: Optional[int] = Field(default=200, description="默认最大每页数量")

    # 方法优化项
    METHOD_TREE_CHOICE: Optional[str] = Field(default="map", description="树状查询方式{sql: sql循环查询,map: 内存查询}")

    # 缓存配置参数
    CACHE_GET_ONE_WHETHER_OPEN: Optional[bool] = Field(default=False, description="查询详情是否打开缓存")
    CACHE_GET_ONE_SECONDS: int = Field(default=300, description="查询详情缓存时间，单位秒")
    CACHE_GET_ALL_WHETHER_OPEN: Optional[bool] = Field(default=False, description="查询列表是否打开缓存")
    CACHE_GET_ALL_SECONDS: int = Field(default=300, description="查询列表缓存时间，单位秒")
    CACHE_TREE_WHETHER_OPEN: Optional[bool] = Field(default=False, description="树状查询是否打开缓存")
    CACHE_TREE_SECONDS: int = Field(default=3600, description="树状查询缓存时间，单位秒")

    # 路由后缀字段是否添加以及配置默认值
    ROUTER_WHETHER_UNDERLINE_TO_STRIKE: Optional[bool] = Field(default=False, description="路由是否下划线转中划线")
    ROUTER_WHETHER_ADD_SUFFIX: Optional[bool] = Field(default=True, description="增删改查路由是否添加后缀")
    ROUTER_CREATE_SUFFIX_FIELD: Optional[str] = Field(default="create", description="创建路由后缀字段")
    ROUTER_GET_ONE_SUFFIX_FIELD: Optional[str] = Field(default="detail", description="获取一个路由后缀字段")  # get_one
    ROUTER_GET_ALL_SUFFIX_FIELD: Optional[str] = Field(default="list", description="获取列表路由后缀字段")   # get_all
    ROUTER_GET_TREE_SUFFIX_FIELD: Optional[str] = Field(default="tree", description="获取树状数据路由后缀字段")  # get_tree
    ROUTER_UPDATE_SUFFIX_FIELD: Optional[str] = Field(default="update", description="修改路由后缀字段")
    ROUTER_DELETE_SUFFIX_FIELD: Optional[str] = Field(default="delete", description="删除路由后缀字段")
    ROUTER_RECURSION_DELETE_SUFFIX_FIELD: Optional[str] = Field(default="delete_tree", description="递归删除路由后缀字段")
    ROUTER_FILTER_DELETE_SUFFIX_FIELD: Optional[str] = Field(default="delete_filter", description="递归删除路由后缀字段")

    # 函数转换路由时，默认添加字段，（遵循restful规范时，get路由处理方案）
    RESTFUL_GET_ROUTER_ADD_PREFIX: Optional[str] = Field(default="", description="函数转换路由时：前缀添加字段")
    RESTFUL_GET_ROUTER_ADD_SUFFIX: Optional[str] = Field(default="", description="函数转换路由时：后缀pk前添加字段")
    RESTFUL_POST_ROUTER_ADD_PREFIX: Optional[str] = Field(default="", description="函数转换路由时：前缀添加字段")
    RESTFUL_POST_ROUTER_ADD_SUFFIX: Optional[str] = Field(default="", description="函数转换路由时：后缀pk前添加字段")
    RESTFUL_PUT_ROUTER_ADD_PREFIX: Optional[str] = Field(default="", description="函数转换路由时：前缀添加字段")
    RESTFUL_PUT_ROUTER_ADD_SUFFIX: Optional[str] = Field(default="", description="函数转换路由时：后缀pk前添加字段")
    RESTFUL_DELETE_ROUTER_ADD_PREFIX: Optional[str] = Field(default="", description="函数转换路由时：前缀添加字段")
    RESTFUL_DELETE_ROUTER_ADD_SUFFIX: Optional[str] = Field(default="", description="函数转换路由时：后缀pk前添加字段")

    # 分布式id
    WORKER_ID: Optional[int] = Field(default=1, description="数据中心（机器区域）ID")
    DATACENTER_ID: Optional[int] = Field(default=1, description="机器ID")

    # 数据库字段默认值
    WHETHER_DELETE_FIELD: Optional[str] = Field(default="deleted_at", description="是否删除字段;推荐命名 >> deleted_at;is_active")
    DELETE_FIELD_TYPE: Optional[str] = Field(default="time", description="删除字段类型;推荐命名 >> time;bool")
    # ACTIVE_DEFAULT_VALUE: Optional[bool] = Field(default=True, description="有效的默认值")
    GET_EXCLUDE_ACTIVE_VALUE: Optional[bool] = Field(default=True, description="查询结果是否排除有效字段")
    CREATE_EXCLUDE_ACTIVE_VALUE: Optional[bool] = Field(default=True, description="创建是否排除有效字段")
    UPDATE_EXCLUDE_ACTIVE_VALUE: Optional[bool] = Field(default=True, description="修改是否排除有效字段")
    DEFAULT_TREE_PARENT_FIELD: Optional[str] = Field(default="parent", description="默认递归父级字段")
    DEFAULT_TREE_CHILDREN_FIELD: Optional[str] = Field(default="children", description="默认递归子级字段")
    DEFAULT_TREE_FILTER_FIELD: Optional[str] = Field(default="node_id", description="默认递归筛选开始节点字段")

    # 返回格式字段配置默认值
    CODE_RESPONSE_FIELD: Optional[bool] = Field(default=True, description="code返回字段")
    CODE_SUCCESS_DEFAULT_VALUE: Optional[int] = Field(default=200, description="code成功返回值")
    CODE_FAIL_DEFAULT_VALUE: Optional[int] = Field(default=-1, description="code失败返回值")
    SUCCESS_RESPONSE_FIELD: Optional[bool] = Field(default=True, description="success返回字段")
    MESSAGE_RESPONSE_FIELD: Optional[str] = Field(default="msg", description="消息返回字段")
    DATA_RESPONSE_FIELD: Optional[str] = Field(default="data", description="数据返回字段")
    LIST_RESPONSE_FIELD: Optional[str] = Field(default="list", description="列表页返回字段")

    # GetAll 筛选是否双下划线转单下划线
    FILTER_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE: Optional[bool] = Field(default=True, description="筛选是否双下划线转单下划线")
    SCHEMAS_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE: Optional[bool] = Field(default=True, description="序列化字段是否双下划线转单下划线")

    class Config:
        env_prefix = "APP_"
        env_file = "./.env"
        case_sensitive = True
        extra = 'allow'



