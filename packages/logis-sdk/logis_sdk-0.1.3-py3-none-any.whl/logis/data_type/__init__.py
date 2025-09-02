from decimal import Decimal
from numbers import Number
from typing import Callable, NewType, Optional, Tuple, TypeAlias, TypeVar, Union

from pydantic import ConfigDict

StringNumber: TypeAlias = str

ComponentIntId: TypeAlias = int

ComponentStrId: TypeAlias = str

ComponentId: TypeAlias = Union[ComponentIntId, ComponentStrId]

TmpId: TypeAlias = Union[int, str]


T = TypeVar("T")
Predicate: TypeAlias = Callable[[T], bool]

Unit = NewType("Unit", str)

# 倍率计算器，输入源单位、目标单位，输出倍率
RatioComputer: TypeAlias = Callable[[Unit, Unit], Decimal]

EventType = NewType("EventType", str)
TaskType = NewType("TaskType", str)

TuplePoint: TypeAlias = Tuple[Optional[Number], Optional[Number], Optional[Number]]

DEFAULT_PYDANTIC_MODEL_CONFIG = ConfigDict(arbitrary_types_allowed=True)

from .point import *

__doc__ = """
类型模块
"""
