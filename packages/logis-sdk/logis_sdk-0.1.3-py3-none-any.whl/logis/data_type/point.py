from itertools import count
from typing import Optional, Tuple

from logis.data_type import Number, TuplePoint


class Point:
    """
    支持x,y,z三维坐标点，也可当作二维坐标使用
    TODO: 处理单位
    """

    __counter = count(0, step=1)

    @classmethod
    def try_parse(cls, dc: dict) -> "Point":
        """
        尝试读取X、Y、Z坐标，返回一个Point对象
        """
        if not isinstance(dc, dict):
            raise TypeError("Expected a dictionary for Point parsing.")
        xyz = [dc.get(k, None) for k in ("X", "Y", "Z")]
        return Point(xyz)

    @classmethod
    def of(
        cls,
        x: Number | None = None,
        y: Number | None = None,
        z: Optional[Number] = None,
        unit: str | None = None,
    ) -> "Point":
        p = Point()
        p.x = x
        p.y = y
        p.z = z
        p.unit = unit
        return p

    def __init__(self, *args, **kwargs):
        """
        支持[x,y]、x,y、[x,y,z]、x,y,z传参赋值
        默认x=y=z=0

        TODO: 不应该自动转float、不应该自动保留两位小数
        """
        self._id = next(self.__counter)
        self.unit: str | None = None
        self.x: Optional[Number] = None
        self.y: Optional[Number] = None
        self.z: Optional[Number] = None
        if len(args) == 1:
            self.x = round(float(args[0][0]), 2)
            self.y = round(float(args[0][1]), 2)
            if len(args[0]) > 2 and (z := args[0][2]) is not None:
                self.z = round(float(z), 2)

        elif len(args) >= 2:
            self.x = round(float(args[0]), 2)
            self.y = round(float(args[1]), 2)
            if len(args) > 2 and (z := args[2]) is not None:
                self.z = round(float(z), 2)

        # 调试过程中发现z有时候是None有时候是0，因此这里统一给了默认值
        # 实际上应该外层规范
        self.x = self.x if self.x is not None else 0
        self.y = self.y if self.y is not None else 0
        self.z = self.z if self.z is not None else 0

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False

    def __lt__(self, other):
        """
        FIXME: 考虑z
        """
        if isinstance(other, Point):
            # TODO: 只要任何一个大于就行？
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented

    def __sub__(self, other: "Point"):
        def sub(a: Number, b: Number):
            if a is None and b is None:
                return None
            a = a or 0
            b = b or 0
            return a - b

        assert self.unit == other.unit, "unit must be same"
        return Point.of(
            x=sub(self.x, other.x),
            y=sub(self.y, other.y),
            z=sub(self.z, other.z),
            unit=self.unit,
        )

    def to_tuple(self) -> TuplePoint:
        return (
            self.x,
            self.y,
            self.z,
        )

    def __str__(self):
        return f"Point(id={self._id},x={self.x},y={self.y},z={self.z})"


if __name__ == "__main__":
    # printPoint(1,2))
    # printPoint([1,2,3,4,5,6,7]))
    # printPoint((1,2,3)))
    pass
