from typing import Any

import simpy


def try_put(
    env: simpy.Environment,
    container: simpy.Container,
    amount: int | float,
    timeout: int | None = None,
):
    x = container.put(amount)
    if timeout:
        x = x | env.timeout(0.1)
    v = yield x
    return v


def resize_container(container: simpy.Container, capacity: int | float, is_delta=False):
    capacity = capacity + container.capacity if is_delta else capacity
    container._capacity = capacity
    # return simpy.Container(container._env, capacity, container.level)


def resource_to_dict(resource: Any):
    if isinstance(resource, simpy.Container):
        return dict(level=resource.level, capacity=resource.capacity)
    if isinstance(resource, simpy.Resource):
        return dict(level=resource.count, capacity=resource.capacity)
    if isinstance(resource, simpy.Store):
        return dict(level=len(resource.items), capacity=resource.capacity)
    print("unexpected type:" + resource)
