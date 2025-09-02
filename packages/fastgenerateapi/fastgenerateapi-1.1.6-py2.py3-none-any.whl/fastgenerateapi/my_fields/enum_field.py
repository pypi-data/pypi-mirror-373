from enum import IntEnum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from fastapi import HTTPException
from tortoise.fields.data import IntEnumFieldInstance

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model


class IntEnumField(IntEnumFieldInstance):
    """
    传入参数数组，默认生成枚举类，数字从 1 开始
    例如：
        enum_list = ["A", "B"]
    相当于枚举
        class CategoryEnum(IntEnum):
            zero = 0
            one = 1
    通过方法 get_name 获取对应的值， "A"
    """

    def __init__(self, enum_list: List[any], **kwargs: Any) -> None:
        self.enum_list = enum_list
        self.description = kwargs.get("description", "") + " >> " + self.get_description(enum_list)
        super().__init__(enum_type=self.create_enum(enum_list), **kwargs)

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": len(self.enum_list),
        }

    def to_db_value(self, value: Any, instance: "Union[Type[Model], Model]") -> Any:
        """
        Converts from the Python type to the DB type.
        """
        if value is not None:
            if isinstance(value, IntEnumClass):
                value = value.value
            value = int(value)  # pylint: disable=E1102
            if value > len(self.enum_list) or 0 > value:
                raise HTTPException(detail=f"枚举值：{value} 校验失败。【{self.description}】", status_code=422)
        self.validate(value)
        return value

    def to_python_value(self, value: Any) -> Any:
        """
        Converts from the DB type to the Python type.
        """
        if value is not None:
            value = int(value)  # pylint: disable=E1102
        self.validate(value)
        return IntEnumClass(value, self.enum_list)

    def get_description(self, enum_list):
        description = ""
        for index, val in enumerate(enum_list, 1):
            description += f"{index}:{val};"
        return description

    def create_enum(self, enum_list):
        # 创建枚举类的成员字典，确保值是唯一的

        members = {self.number_to_words(name): name for name, _ in enumerate(enum_list, 0)}

        # 使用Enum的元类EnumMeta来动态创建枚举类
        enum_class = IntEnum("CategoryEnum", members)

        # 返回创建的枚举类
        return enum_class

    @classmethod
    def number_to_words(cls, num):
        # 定义数字到单词的映射
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

        if num == 0:
            return 'zero'

        if num < 20:
            return ones[num]

        if num < 100:
            ten_digit = num // 10
            one_digit = num % 10
            if one_digit == 0:
                return tens[ten_digit]
            else:
                return tens[ten_digit] + '_' + ones[one_digit]

        if num < 1000:
            hundred_digit = num // 100
            remaining = num % 100
            return ones[hundred_digit] + '_hundred_' + cls.number_to_words(remaining)

            # 对于大于1000的数字，可以进一步扩展这个函数来处理
        # 但请注意，标准的英文数字读法会变得复杂，涉及"thousand", "million", "billion"等词

        # 这里仅处理到9999，如果需要处理更大的数字，请继续扩展这个函数
        thousand_digit = num // 1000
        remaining = num % 1000
        return cls.number_to_words(thousand_digit) + '_thousand_' + cls.number_to_words(remaining)


class IntEnumClass:
    def __init__(self, value: int, name_list: list):
        self.value = value
        self.name_list = name_list

    def __str__(self):
        return f"{self.value}"

    def __int__(self):
        return self.value

    @property
    def name(self):
        try:
            return self.name_list[self.value]
        except:
            return self.value

    def __add__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return IntEnumClass(self.value + other.value, self.name_list)
        elif isinstance(other, int):
            return IntEnumClass(self.value + other, self.name_list)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'NamedInt' and '{type(other).__name__}'")

    def __sub__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return IntEnumClass(self.value - other.value, self.name_list)
        elif isinstance(other, int):
            return IntEnumClass(self.value - other, self.name_list)
        else:
            raise TypeError(f"unsupported operand type(s) for -: 'IntEnumClass' and '{type(other).__name__}'")

    def __mul__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return IntEnumClass(self.value * other.value, self.name_list)
        elif isinstance(other, int):
            return IntEnumClass(self.value * other, self.name_list)
        else:
            raise TypeError(f"unsupported operand type(s) for *: 'IntEnumClass' and '{type(other).__name__}'")

    def __truediv__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            if other.value == 0:
                raise ZeroDivisionError("division by zero")
            return IntEnumClass(self.value // other.value, self.name_list)
        elif isinstance(other, int):
            if other == 0:
                raise ZeroDivisionError("division by zero")
            return IntEnumClass(self.value // other, self.name_list)
        else:
            raise TypeError(f"unsupported operand type(s) for /: 'IntEnumClass' and '{type(other).__name__}'")

    def __eq__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return self.value == other.value
        elif isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __ne__(self, other: Union["IntEnumClass", int]):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        return NotImplemented

    def __le__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return self.value <= other.value
        elif isinstance(other, int):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return self.value > other.value
        elif isinstance(other, int):
            return self.value > other
        return NotImplemented

    def __ge__(self, other: Union["IntEnumClass", int]):
        if isinstance(other, IntEnumClass):
            return self.value >= other.value
        elif isinstance(other, int):
            return self.value >= other
        return NotImplemented





