import math

SCREEN_HEIGHT = 5000
SCREEN_WIDTH = 5000
POLYGON_COUNT = 60
OBSTACLE_COUNT = 10
CLUSTER_SIZE = 10
CLUSTER_RADIUS = 800
DATEI_NAME = ""

ANTIALIAS_FACTOR = 4
FONT_SIZE = 20
OFFSET = 30

GUROBI_MAX_TIME = 60  # sek


IMAGE_PRE = "image/"
INSTANCES_PRE = "instances/"
FONT_PRE = "font/"


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}:{self.y})"

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        return iter((self.x, self.y))


class Edge:
    def __init__(self, point1: Coord, point2: Coord) -> None:
        self.point1 = point1
        self.point2 = point2
        self.length = calculate_distance(self.point1, self.point2)

    def __str__(self) -> str:
        return f"{self.point1}{self.point2} der Länge: {self.length}"

    def __repr__(self) -> str:
        return str(self)


class Polygon:
    def __init__(self, hull: list[Coord]) -> None:
        if len(hull) < 3:
            raise ValueError("Ein Polygon benötigt mindestens 3 Punkte.")
        self.hull = hull
        self.centroid = calculate_centroid(self.hull)

    def __str__(self) -> str:
        return f"{self.hull} mit Schwerpunkt: {self.centroid}"


class Stats:
    def __init__(self, dist, angle) -> None:
        self.dist = dist
        self.angle = angle


def calculate_distance(point1: Coord, point2: Coord) -> float:
    distance = math.sqrt(
        math.pow((point1.x - point2.x), 2) +
        math.pow((point1.y - point2.y), 2)
    )
    return distance


def to_coord(points) -> list[Coord]:
    coords = []
    for point in points:
        coords.append(Coord(int(point[0]), int(point[1])))
    return coords


def make_edges(points: list[Coord]) -> list[Edge]:
    result = []
    for i in range(len(points)):
        result.append(Edge(points[i], points[(i + 1) % len(points)]))
    return result


def calculate_centroid(hull: list[Coord]) -> Coord:
    """Berechnet den Schwerpunkt eines Polygons"""
    x = 0
    y = 0
    for i in range(len(hull)):
        x += hull[i].x
        y += hull[i].y
    centroid = Coord(int(x / len(hull)), int(y / len(hull)))
    return centroid


def prints_stats(name: str, dis, angle):
    print(f"Distance: {round(dis, 2)}\tAngle: {round(angle, 2)}\t{name}")
