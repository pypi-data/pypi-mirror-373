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
from tortoise.fields import Field

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model

from fastgenerateapi.utils.snowflake import worker


class PrimaryKeyField(Field[str], str):
    """
    Big integer field. (64-bit signed)
    """

    SQL_TYPE = "BIGINT"
    allows_generated = True

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("description", "主键")
        kwargs.setdefault("default", worker.get_id)
        super().__init__(**kwargs)

    def to_db_value(self, value: Any, instance: "Union[Type[Model], Model]") -> Any:
        """
        Converts from the Python type to the DB type.
        """
        if value is not None:
            value = int(value)  # pylint: disable=E1102
        self.validate(value)
        return value

    def to_python_value(self, value: Any) -> Any:
        """
        Converts from the DB type to the Python type.
        """
        if value is not None:
            value = str(value)  # pylint: disable=E1102
        self.validate(value)
        return value














