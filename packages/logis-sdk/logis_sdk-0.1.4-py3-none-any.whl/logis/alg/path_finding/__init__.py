from abc import ABCMeta, abstractmethod
from inspect import isclass
from typing import TYPE_CHECKING, Type

from pathfinding.finder.finder import Finder

from .model import *

__doc__ = "寻路算法模块"

if TYPE_CHECKING:
    pass


class PathFindingAlgorithm(metaclass=ABCMeta):
    """
    寻路算法
    """

    type: PathFindingAlgorithmType | str

    @abstractmethod
    def find_path(self, input: PathFindingInput, **kwargs) -> PathFindingOutput:
        """
        寻找从start到end的路径
        """
        pass


def default_algorithm_matcher(alg_name: str) -> PathFindingAlgorithmType:
    """
    默认算法匹配器
    根据输入的类型匹配对应的寻路算法
    如果找不到，则返回默认的A*算法
    """
    if alg_name == "default":
        return A_STAR_ALGORITHM

    for _, v in globals().items():
        if isinstance(v, str) and v == alg_name:
            return v
    return A_STAR_ALGORITHM


def get_algorithm(type: PathFindingAlgorithmType) -> Type[PathFindingAlgorithm]:
    """
    根据类型获取对应的寻路算法类
    """
    # TODO：支持热加载模块
    for _, value in globals().items():
        if (
            isclass(value)
            and issubclass(value, PathFindingAlgorithm)
            and getattr(value, "type", None) == type
        ):
            return value
    raise ValueError(f"Unknown pathfinding algorithm type: {type}")


def find_algorithm(resolver: AlgorithmTypeResolver, **kwargs):
    """
    根据解析器和参数获取对应的寻路算法类

    Args:
        resolver: 解析器函数
        kwargs: 解析器需要的参数
    """
    type = resolver(**kwargs)
    return get_algorithm(type)


if __name__ == "__main__":
    pass
