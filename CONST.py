SCREEN_HEIGHT = 6000
SCREEN_WIDTH = 6000
AREA_COUNT = 40
CLUSTER_SIZE = 10
MIN_DISTANCE_AREA = 1500
MIN_DISTANCE_CLUSTER = 30
CLUSTER_RADUIS = 200
DATEI_NAME = "test"

ANTIALIAS_FACTOR = 4
FONT_SIZE = 20
OFFSET = 30

OPT_TURN_COST = True


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}:{self.y})"

    def __repr__(self) -> str:
        return str(self)


class Edge:
    def __init__(self, point1: Coord, point2: Coord, length: float = 0) -> None:
        self.point1 = point1
        self.point2 = point2
        self.length = length

    def __str__(self) -> str:
        return f"{self.point1}{self.point2} der Länge: {self.length}"

    def __repr__(self) -> str:
        return str(self)
