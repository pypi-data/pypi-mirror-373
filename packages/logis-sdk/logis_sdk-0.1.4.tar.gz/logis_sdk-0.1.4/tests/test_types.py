from logis.data_type import Point


def test_point():
    p1 = Point(1, 2)
    p2 = Point(1, 2, 3)
    p3 = Point([1, 2, 3])
    p4 = Point([10, 1])
    for p in [p1, p2, p3, p4]:
        print(p)

    assert p1 - p2 == Point(0, 0, -3)
    assert p3 - p4 == Point(-9, 1, 3)
    assert Point() - Point() == Point()
