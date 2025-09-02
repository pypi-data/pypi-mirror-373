from typing import Callable, List, Optional, Sequence, TypeVar, Dict, Union, Type

from fastapi import Depends

from fastgenerateapi.pydantic_utils.base_model import BaseModel


PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]

CALLABLE = Callable[..., BaseModel]
CALLABLE_LIST = Callable[..., List[BaseModel]]
RESPONSE_WRAPPER = Callable[
    [
        Union[
            Type[T],
            BaseModel
        ],
        int,
        str,
        str,
        bool,
        Union[
            Type[T],
            str
        ]
    ],
    Union[
        Type[T],
        BaseModel
    ]
]



