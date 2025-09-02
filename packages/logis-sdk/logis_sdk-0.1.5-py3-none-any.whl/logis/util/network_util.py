from typing import List, Tuple, TypeAlias

from logis.data_type import Point

Grid2: TypeAlias = List[List[Point]]
Grid3: TypeAlias = List[Grid2]


def to_grid(
    points: List[Point], include_x=True, include_y=True, include_z=False, **kwargs
) -> Grid3 | Grid2 | None:
    """
    将一系列点转换为网格结构
    每个Point代表一个方块的中心点，方块大小一致但不一定是正立方体

    Args:
        points: 一系列Point对象
        **kwargs: 可选参数
            x_step: x方向上的网格步长,如果未指定则自动推测
            y_step: y方向上的网格步长,如果未指定则自动推测
            z_step: z方向上的网格步长,如果未指定则自动推测

    Returns:
        三维网格/二维网格
    """
    if not points:
        return None

    # 定义一个函数来计算步长
    def calculate_step(values):
        """计算一组值的最小步长"""
        if len(values) <= 1:
            return 1

        # 计算相邻值之间的差值
        diffs = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
        return min(diffs)

    x_step = y_step = z_step = None
    x_size = y_size = z_size = None

    # 获取步长参数，如果未指定则自动计算
    if include_x:
        x_step = kwargs.get("x_step", calculate_step(sorted(set(p.x for p in points))))
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        x_size = int((max_x - min_x) / x_step) + 1

    if include_y:
        y_step = kwargs.get("y_step", calculate_step(sorted(set(p.y for p in points))))
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        y_size = int((max_y - min_y) / y_step) + 1

    if include_z:
        z_step = kwargs.get("z_step", calculate_step(sorted(set(p.z for p in points))))
        min_z = min(p.z for p in points)
        max_z = max(p.z for p in points)
        z_size = int((max_z - min_z) / z_step) + 1

    valid_indexes = list(filter(lambda v: v is not None, [x_size, y_size, z_size]))
    if len(valid_indexes) < 2:
        return None

    # 初始化网格
    if x_size and y_size and z_size:
        grid = [
            [[None for _ in range(z_size)] for _ in range(y_size)]
            for _ in range(x_size)
        ]
    else:
        x_size, y_size = valid_indexes
        grid = [[None for _ in range(y_size)] for _ in range(x_size)]

    # 将点放入网格中
    for point in points:
        # 计算点在网格中的索引
        x_idx = int((point.x - min_x) / x_step) if x_step else None
        y_idx = int((point.y - min_y) / y_step) if y_step else None
        z_idx = int((point.z - min_z) / z_step) if z_step else None

        tmp = grid
        for _, idx in enumerate([x_idx, y_idx, z_idx]):
            if idx is None:
                continue
            if tmp[idx] is None:
                tmp[idx] = point
            else:
                tmp = tmp[idx]
    return grid


if __name__ == "__main__":
    grid1 = to_grid(
        [Point.of(0, 0, 0), Point.of(1, 1.5, 1), Point.of(2, 2, 2)], include_z=False
    )
    print(grid1)
