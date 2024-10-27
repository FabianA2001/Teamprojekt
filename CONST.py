SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1000
COUNT = 50
DATEI_NAME = "test"


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Edge:
    def __init__(self, point1: Coord, point2: Coord, length: float = 0) -> None:
        self.point1 = point1
        self.point2 = point2
        self.length = length
