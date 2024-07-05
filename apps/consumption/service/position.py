import collections


PositionTuple = collections.namedtuple("PositionTuple", ("x", "y", "z"))


class Position(PositionTuple):
    @staticmethod
    def middle(positions: list["Position"]) -> "Position":
        x = sum(x.x for x in positions) / len(positions)
        y = sum(x.y for x in positions) / len(positions)
        z = sum(x.z for x in positions) / len(positions)
        return Position(int(x), int(y), int(z))

    def distance(self, other: "Position") -> float:
        print(len(Position))
        return 1
