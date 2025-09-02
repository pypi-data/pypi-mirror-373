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

from fastgenerateapi.utils.aes import AESCipher

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model


class AESField(CharField):
    """
    Character field.

    You need provide the following:

    ``salt`` (str): must
        CBC加密需要一个十六位的key(密钥)和一个十六位iv(偏移量)
    ``is_decrypt`` (str): default True 明文
        返回结果是否明文
    ``prefix`` (str): default $aes_
        判断是否加密
    """

    def __init__(self, salt: str, is_decrypt: bool = True, prefix="$aes_", **kwargs: Any) -> None:
        kwargs.setdefault("max_length", 255)
        kwargs.setdefault("description", "加密字段")
        self.salt = salt
        self.prefix = prefix
        self.is_decrypt = is_decrypt
        super().__init__(**kwargs)

    def to_db_value(self, value: Any, instance: "Union[Type[Model], Model]") -> Any:
        """
        Converts from the Python type to the DB type.
        """
        if value is not None:
            if not isinstance(value, self.field_type):
                value = self.field_type(value)  # pylint: disable=E1102
            if not value.startswith(self.prefix):
                value = self.prefix + AESCipher(self.salt).encrypt(value).decode("utf-8")

        self.validate(value)
        return value

    def to_python_value(self, value: Any) -> Any:
        """
        Converts from the DB type to the Python type.
        """
        if value is not None:
            if not isinstance(value, self.field_type):
                value = self.field_type(value)  # pylint: disable=E1102
            if value.startswith(self.prefix):
                value = AESString(value[len(self.prefix):], self.salt, self.is_decrypt)

        self.validate(value)
        return value


class AESString(object):
    def __init__(self, value: str, salt: str, is_decrypt: bool = True):
        self.value = value
        self.salt = salt
        self.is_decrypt = is_decrypt

    def __str__(self):
        if self.is_decrypt:
            return self.decrypt_value
        return self.value

    @property
    def decrypt_value(self):
        return AESCipher(self.salt).decrypt(self.value).decode("utf-8")

    def __len__(self):
        return len(str(self))

    def __getitem__(self, index):
        return str(self)[index]

    def __add__(self, other: Union["AESString", str]):
        if isinstance(other, AESString):
            other = str(other)
        return str(self) + other

    def __contains__(self, substring):
        return substring in str(self)

    def find(self, substring, start=0, end=None):
        return str(self).find(substring, start, end)

    def index(self, substring, start=0, end=None):
        return str(self).index(substring, start, end)

    def split(self, sep=None, maxsplit=-1):
        return str(self).split(sep, maxsplit)

    def replace(self, old, new, count=-1):
        return str(self).replace(old, new, count)

    def startswith(self, prefix, start=0, end=None):
        return str(self).startswith(prefix, start, end)

    def endswith(self, suffix, start=0, end=None):
        return str(self).endswith(suffix, start, end)

    def __mul__(self, n):
        return str(self) * n

    def __rmul__(self, n):
        return self.__mul__(n)

    def capitalize(self):
        return str(self).capitalize()

    def title(self):
        return str(self).title()

    def upper(self):
        return str(self).upper()

    def lower(self):
        return str(self).lower()

    def swapcase(self):
        return str(self).swapcase()

    def strip(self, chars=None):
        return str(self).strip(chars)

    def lstrip(self, chars=None):
        return str(self).lstrip(chars)

    def rstrip(self, chars=None):
        return str(self).rstrip(chars)

    def count(self, sub, start=0, end=None):
        return str(self).count(sub, start, end)

    def join(self, iterable):
        return str(self).join(iterable)

    def encode(self, encoding='utf-8', errors='strict'):
        return str(self).encode(encoding, errors)








