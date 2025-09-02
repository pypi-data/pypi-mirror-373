from datetime import datetime, date, time
from typing import Union, Any, Optional

from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.settings.all_settings import settings


class FilterUtils:

    @staticmethod
    def date_to_datetime_23(date_value: Union[None, str, date, datetime]) -> Optional[datetime]:
        """
        使用场景：如创建时间筛选2025-01-01 至 2025-12-31；由于储存数据为datetime类型，会导致2025-12-31当天数据不包含
        :param cls:
        :param date_value:
        :return:
        """
        if date_value is None:
            return None

        # 如果 date_value 是字符串，尝试解析为日期
        if isinstance(date_value, str):
            try:
                # 尝试解析为 date 类型，这里假设日期字符串的格式是 YYYY-MM-DD
                parsed_date = datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                # 如果解析失败，则尝试解析为 datetime 类型（可能包含时间信息）
                try:
                    parsed_datetime = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                    parsed_date = parsed_datetime.date()
                except ValueError:
                    # 如果仍然失败，则返回 None
                    return None

        # 如果 date_value 已经是 date 类型，直接使用
        elif isinstance(date_value, date):
            parsed_date = date_value

        # 其他类型返回 None
        else:
            return None

        # 将日期加上时间 "23:59:59" 转换为 datetime 类型
        result_datetime = datetime.combine(parsed_date, datetime.min.time().replace(hour=23, minute=59, second=59))
        return result_datetime


class BaseFilter:
    """
        BaseFilter
    """

    def __init__(self, filter_str: Union[str, tuple]):
        """
        :param filter_str:  Union[str, tuple]
            当tuple时，第一个为str，后面参数无顺序和数量要求，可以是 类型、重命名字符串、用于修改传值的方法
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
        """
        field_type = str
        model_field = filter_str
        filter_field = None
        filter_func = None
        # 判断filter表达式的类型
        if isinstance(filter_str, tuple):
            model_field = filter_str[0]
            filter_field = filter_str[0]
            for f in filter_str[1:]:
                if type(f) == type:
                    field_type = f
                    continue
                if type(f) == str:
                    filter_field = f
                    continue
                if callable(f):
                    filter_func = f
        if not filter_field:
            if settings.app_settings.FILTER_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE:
                filter_field = model_field.replace("__", "_")
            else:
                filter_field = model_field

        self.field_type = field_type
        self.model_field = model_field
        self.filter_field = filter_field
        self.filter_func = filter_func

    def generate_q(self, value: Union[str, list, bool]) -> Q:
        """
            生成Q查询对象
        :param value:
        :return:
        """
        if isinstance(value, (str, datetime, date, time)):
            if hasattr(value, "upper") and value.upper() in ["NONE", "NULL", "NIL"]:
                return eval(f"Q({self.model_field}={None})")
            return eval(f"Q({self.model_field}='{value}')")
        return eval(f"Q({self.model_field}={value})")

    def query(self, queryset: QuerySet, value: Union[str, list, bool]) -> QuerySet:
        """
            do query action
        :param queryset:
        :param value:
        :return:
        """
        if self.filter_func:
            value = self.filter_func(value)
        queryset = queryset.filter(self.generate_q(value=value))
        return queryset


class FilterController:
    """
        FilterController
    """

    def __init__(self, filters: list[BaseFilter]):
        self.filters = filters
        self.filter_map: dict[str, BaseFilter] = {}
        for f in self.filters:
            self.filter_map[f.filter_field] = f

    def query(self, queryset: QuerySet, values: dict[str, Any]) -> QuerySet:
        """
            do query action
        :param queryset:
        :param values:
        :return:
        """
        for k in values:
            f = self.filter_map.get(k, None)
            v = values[k]
            if f is not None and (v or v == 0 or isinstance(v, bool)):
                queryset = f.query(queryset=queryset, value=v)

        return queryset

    def is_empty(self) -> bool:
        return len(self.filters) == 0













