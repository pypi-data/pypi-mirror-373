import datetime
import re

from tortoise.validators import Validator

from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin


class BlankStringValidator(Validator):
    """
    不允许空字符串校验
    """
    def __init__(self, description: str):
        self.description = description

    def __call__(self, value: str):
        if isinstance(value, str):
            value = value.strip()
        if not value:
            return ResponseMixin.error(status_code=422, message=f"{self.description}不能为空")


class IDCardValidator(Validator):
    """
    身份证校验
    """

    def __call__(self, value: str):
        if len(value) == 15:
            return value
        if len(value) != 18:
            return ResponseMixin.error(message="身份证输入错误")
        this_year = datetime.datetime.now().year
        if int(value[6:10]) < 1000 or int(value[6:10]) > this_year:
            return ResponseMixin.error(message="身份证输入错误")
        if int(value[10:12]) < 1 or int(value[10:12]) > 12 or int(value[12:14]) < 1 or int(value[12:14]) > 31:
            return ResponseMixin.error(message="身份证输入错误")
        arg_list = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_list = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]
        sum_num = 0
        for index, num in enumerate(value[:-1]):
            sum_num += arg_list[index] * int(num)
        if value[-1] != check_list[sum_num % 11]:
            return ResponseMixin.error(message=f"身份证: {value} 输入错误")
        return value


class PhoneValidator(Validator):
    """
    手机号码校验
    """

    def __call__(self, value: str):
        ret = re.compile('^(?:(?:\+|00)86)?1[3-9]\d{9}$')
        res = ret.match(value)
        if res:
            return res.group()
        return ResponseMixin.error(message="手机号码校验不通过")


