from collections import defaultdict
from decimal import Decimal
from functools import reduce
from numbers import Number
from typing import Callable, List, NewType, Tuple, TypeAlias

from pydantic import BaseModel

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG as MODEL_CONFIG
from logis.data_type import (
    RatioComputer,
    Unit,
)

from .point import *


class NumberUnit(BaseModel):
    model_config = MODEL_CONFIG

    quantity: Number | Decimal
    unit: Unit | None = None

    # 自定义倍率转换器
    _ratio_computer: RatioComputer | None = None

    def __auto_validate__(self, other: "NumberUnit"):
        if self._ratio_computer is None:
            assert self.unit == other.unit, "unit must be the same"
        else:
            other = unify_quantified_value(other, self.unit, self._ratio_computer)
        return other

    def __sub__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return type(self)(quantity=self.quantity - other.quantity, unit=self.unit)

    def __add__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return type(self)(quantity=self.quantity + other.quantity, unit=self.unit)

    def __truediv__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        # TODO: 处理精度问题
        return self.quantity / other.quantity

    def __gt__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return self.quantity > other.quantity

    def __lt__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return self.quantity < other.quantity

    def __eq__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return self.quantity == other.quantity

    def __ge__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return self.quantity >= other.quantity

    def __le__(self, other: "NumberUnit"):
        other = self.__auto_validate__(other)
        return self.quantity <= other.quantity

    @property
    def value(self):
        return self.quantity

    @value.setter
    def value(self, new_value):
        self.quantity = new_value

    @classmethod
    def parse_tuple(cls, input: Tuple[Number, Unit]):
        """
        解析形如[1,"个"]的数据
        """
        return cls(quantity=input[0], unit=input[1])

    @classmethod
    def parse_str(cls, input: str, delimiter="|", number_type=float):
        """
        解析形如1|m/s的数据
        """
        if not input:
            return None
        tmps = input.strip().split(delimiter)
        assert len(tmps) == 2, "unexpected format: " + input
        return cls(quantity=number_type(tmps[0]), unit=tmps[1])

    @classmethod
    def of(cls, num: Number, unit: str | None = None):
        return cls(quantity=num, unit=unit)

    def increase(self, num: Number) -> None:
        self.quantity += num

    def decrease(self, num: Number) -> None:
        self.quantity -= num


# 量化值
QuantifiedValue: TypeAlias = NumberUnit


class Capacity(QuantifiedValue):
    pass


class Length(QuantifiedValue):
    pass


class Speed(QuantifiedValue):
    pass


SpeedVector: TypeAlias = Tuple[Optional[Speed], Optional[Speed], Optional[Speed]]


class ThreeDimensionalVelocity(BaseModel):
    """
    使用x,y,z表示的三维速度
    """

    model_config = MODEL_CONFIG

    x: Speed | None = None
    y: Speed | None = None
    z: Speed | None = None

    @classmethod
    def of(
        cls,
        x: Number | None = None,
        y: Number | None = None,
        z: Number | None = None,
        unit: str | None = None,
    ):
        return cls(
            x=None if x is None else Speed.of(x, unit),
            y=None if y is None else Speed.of(y, unit),
            z=None if z is None else Speed.of(z, unit),
        )


class Time(QuantifiedValue):
    """
    时间
    """

    pass


def get_time(l: Length, v: Speed):
    """
    距离/速度=时间
    TODO：处理单位
    """
    assert l.value is not None, "length is not specified"
    assert v.value is not None, "speed is not specified"
    assert v.value != 0, "speed cannot be zero"
    return abs(l.value / v.value)


def get_time_3d(delta_distance: Point, v: ThreeDimensionalVelocity):
    """
    分别计算各维度的时间，取最大值
    """
    lz, ly, lx, lunit = (
        delta_distance.z,
        delta_distance.y,
        delta_distance.x,
        delta_distance.unit,
    )
    return max(
        0 if lx is None else get_time(Length(quantity=lx, unit=lunit), v.x),
        0 if ly is None else get_time(Length(quantity=ly, unit=lunit), v.y),
        0 if lz is None else get_time(Length(quantity=lz, unit=lunit), v.z),
    )


def default_ratio_computer(src: Unit, dst: Unit) -> Number:
    """
    默认的倍率计算器
    """
    if src == dst:
        return 1
    map = dict(km=10**3, m=1, dm=10**-1, cm=10**-2, mm=10**-3, nm=10**-9)
    map |= dict(kl=10**3, l=1, dl=10**-1, cl=10**-2, ml=10**-3)
    src, dst = src.lower(), dst.lower()
    assert src in map, f"unknown source unit: {src}"
    assert dst in map, f"unknown target unit: {dst}"
    return float(Decimal(map[src]) / Decimal(f"{map[dst]:.20f}"))


def unify_quantified_value(
    self: QuantifiedValue,
    target_unit: Unit | None = None,
    ratio_computer: RatioComputer = default_ratio_computer,
):
    """
    单位转换
    """
    same_unit = self.unit == target_unit
    if ratio_computer is None:
        assert same_unit, "unit must be the same if no radio_computer given"
    else:
        ratio = 1 if same_unit else ratio_computer(self.unit, target_unit)
        dc = self.model_dump() | dict(quantity=self.quantity * ratio, unit=target_unit)
        return type(self)(**dc)


def merge_quantified_value(
    items: List[QuantifiedValue],
    ratio_computer: RatioComputer | None = default_ratio_computer,
    target_unit: Unit | None = None,
):
    """
    将所有的物理量合并，这里是假定所有的物理量都是同类，例如：全是长度，而不是既有长度又有速度

    Args:
        items: 待合并项
        ratio_computer: 倍率计算器
        target_unit: 目标单位，如果未指定，默认使用数组的第一个条目的单位
    """
    assert items, "item length need to be at least 1"
    target_unit = target_unit or items[0].unit
    if len(items) != 2:
        return reduce(
            lambda a, b: merge_quantified_value(
                [a, b], target_unit=target_unit, ratio_computer=ratio_computer
            ),
            items,
        )
    self, other = unify_quantified_value(
        items[0], target_unit=target_unit, ratio_computer=ratio_computer
    ), unify_quantified_value(
        items[1], target_unit=target_unit, ratio_computer=ratio_computer
    )
    dc = self.model_dump() | dict(
        quantity=self.quantity + other.quantity, unit=target_unit
    )
    return type(self)(**dc)


def group_merge_quantified_value(items: List[QuantifiedValue]) -> List[QuantifiedValue]:
    """
    按照单位分组，并合并同类单位物理量
    """
    result = []
    unit_items_map = defaultdict(list)
    for item in items:
        unit_items_map[item.unit].append(item)
    for unit, items in unit_items_map.items():
        result.append(merge_quantified_value(items))
    return result
