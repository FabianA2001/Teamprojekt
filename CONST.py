SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
COUNT = 50
MIN_DISTANCE = 50
DATEI_NAME = "test"


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
