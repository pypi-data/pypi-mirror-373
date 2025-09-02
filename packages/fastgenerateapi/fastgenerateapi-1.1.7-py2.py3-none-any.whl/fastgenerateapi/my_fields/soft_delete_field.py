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
from tortoise.fields import BigIntField

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model


class SoftDeleteField(BigIntField):
    """
    毫秒级时间戳储存
    """

    allows_generated = False

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("index", True)
        kwargs.setdefault("null", True)
        kwargs.setdefault("default", None)
        kwargs.setdefault("description", "软删除")
        super().__init__(**kwargs)

    def to_db_value(self, value: Any, instance: "Union[Type[Model], Model]") -> Any:
        """
        Converts from the Python type to the DB type.
        """
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)  # pylint: disable=E1102
            if value == 0:
                value = None
        self.validate(value)
        return value

    def to_python_value(self, value: Any) -> Any:
        """
        Converts from the DB type to the Python type.
        """
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(value)  # pylint: disable=E1102
        self.validate(value)
        return value


