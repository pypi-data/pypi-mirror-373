from typing import Callable, NewType

from logis.alg.path_finding import Finder
from logis.alg.path_finding.model import (
    PathFindingAlgorithmType,
    PathFindingInput,
)
from logis.data_type import Predicate
from logis.data_type.point import Point


def test_pathfinding_model():
    assert isinstance(PathFindingAlgorithmType, NewType)
    assert isinstance(Predicate, Callable)

    print("Pathfinding model test passed.")

    input = PathFindingInput(start=Point.of(1, 2), end=Point.of(3, 4))
    input.graph


def test_pathfinding_alg():
    pass
