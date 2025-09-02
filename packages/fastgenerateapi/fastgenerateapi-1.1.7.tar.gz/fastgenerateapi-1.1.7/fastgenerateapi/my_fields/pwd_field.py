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

from passlib.handlers.pbkdf2 import pbkdf2_sha256
from tortoise.fields import CharField
if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model


class PasswordField(CharField):
    """
    Character field.

    You must provide the following:

    ``salt`` (str):
    """

    def __init__(self, salt: str, rounds=1000, **kwargs: Any) -> None:
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("description", "密码")
        self.salt = salt
        self.rounds = rounds
        super().__init__(**kwargs)

    def to_db_value(self, value: Any, instance: "Union[Type[Model], Model]") -> Any:
        """
        Converts from the Python type to the DB type.
        """
        if value is not None:
            if not isinstance(value, self.field_type):
                value = self.field_type(value)  # pylint: disable=E1102
            custom_pbkdf2 = pbkdf2_sha256.using(salt=self.salt.encode('utf-8'), rounds=self.rounds)
            value = custom_pbkdf2.hash(value)

        self.validate(value)
        return value

    def to_python_value(self, value: Any) -> Any:
        """
        Converts from the DB type to the Python type.
        """
        if value is not None and not isinstance(value, self.field_type):
            value = PasswordString(self.field_type(value), self.salt, self.rounds)  # pylint: disable=E1102
        self.validate(value)
        return value


class PasswordString(str):
    def __init__(self, password, salt, rounds):
        self.value = password
        self.salt = salt
        self.rounds = rounds
        super().__init__()

    def __str__(self):
        return self.value

    def check_valid(self, password: str) -> bool:
        """
        检查密码是否正确
        """
        custom_pbkdf2 = pbkdf2_sha256.using(salt=self.salt.encode('utf-8'), rounds=self.rounds)
        return self.password == custom_pbkdf2.hash(password)





