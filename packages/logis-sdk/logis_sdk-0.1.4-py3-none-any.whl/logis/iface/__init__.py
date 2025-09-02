from typing import Protocol, runtime_checkable


@runtime_checkable
class Shape(Protocol):
    """
    形状，例如路径、节点等
    """

    pass


@runtime_checkable
class Producer(Protocol):
    """
    生产者
    """

    def produce(self, **kwargs):
        pass


@runtime_checkable
class Consumer(Protocol):
    """
    消费者
    """

    def consume(self, **kwargs):
        pass
