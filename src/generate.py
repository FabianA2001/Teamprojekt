import random
from CONST import Coord, Polygon
import CONST



def cross_product(a: Coord, b:Coord, p:Coord) -> float:
    return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)

def random_coord_global(height: int, width: int) -> Coord:
    OFFSET = (CONST.OFFSET + CONST.CLUSTER_RADIUS) * CONST.ANTIALIAS_FACTOR
    return Coord(random.randint(OFFSET, height - OFFSET), random.randint(OFFSET, width - OFFSET))

def random_coord_local(center: Coord, radius: int) -> Coord:
    return Coord(random.randint(center.x - radius, center.x + radius), random.randint(center.y - radius, center.y + radius))

def random_cluster(center: Coord, count: int) -> list[Coord]:
    cluster = []
    for _ in range(count):
        new_point = random_coord_local(center, CONST.CLUSTER_RADIUS)
        cluster.append(new_point)
    return cluster

def generate_polygons(count: int, height: int, width: int) -> list[Polygon]:
    """
    Generiert zufällige Polygone auf dem Screen.

    :param int count: Die Anzahl an Polygons die generiert wird.
    :param int height: Die Höhe des Bereiches in dem die Polygone generiert werden können.
    :param int width: Die Breite des Bereiches in dem die Polygone generiert werden können.

    :return list[Polygon]: Eine Liste, die die genrierten Polygone enthält.
    """
    polygon_list = []
    for _ in range(count):
        center = random_coord_global(height, width)
        polygon = Polygon(create_convexe_hull(random_cluster(center, CONST.CLUSTER_SIZE)))
        polygon_list.append(polygon)
    return polygon_list


def create_convexe_hull(points: list[Coord]) -> list[Coord]:
    """
    Findet die konvexe Hülle einer Punktmenge mit dem Jarvis-March-Algorithmus.

    :param list[Coord] points: Das Cluster von Punkten für welche die konvexe Hülle generiert werden soll.

    :return list[Coord]: Die Liste mit Koordinaten, die die konvexe Hülle bilden.
    """

    def orientation(current_point: Coord, next_point: Coord, pot_next_point: Coord) -> int:
        """
        Gibt die Orientierung von "pot_next_point" zu "next_point" relativ zu "current_point" an.

        :param Coord current_point: Der aktuelle Punkt der konvexen Hülle.
        :param Coord next_point: Der nächste Punkte der zur konvexen Hülle hinzugefügt werden soll.
        :param Coord pot_next_point: potenzielle Punkte die als nächstes hinzugefügt werden könnten.

        :return int: die Orientierung der Punkte als integer: -1 -> im Uhrzeigersinn, 0 -> kollinear, 1 -> gegen den Uhrzeigersinn    
        """
        cross = cross_product(current_point, next_point, pot_next_point)
        if cross == 0:
            return 0
        return 1 if cross > 0 else -1
    
    start_point = min(points, key = lambda points: (points.x, points.y))
    convexe_hull =[]
    current_point = start_point
    while True:
        convexe_hull.append(current_point)
        next_point = points[0]
        for pot_next_point in points:
            if pot_next_point == current_point:
                continue
            orientation_value = orientation(current_point, next_point, pot_next_point)
            if orientation_value == -1 or (orientation_value == 0 and
                                           CONST.calculate_distance(pot_next_point, current_point)
                                           > CONST.calculate_distance(next_point, current_point)):
                next_point = pot_next_point
        current_point = next_point
        if current_point == start_point:
            break
    return convexe_hull



def is_point_inside_polygon(polygon: Polygon, point: Coord) -> bool:
        """
        Überprüft, ob ein Punkt innerhalb oder auf der Grenze des Polygon liegt.

        :param Polygon polygon: Das zu überprüfende Polygon.
        :param Coord point: Der zu überprüfende Punkt.
        :return bool: True, wenn der Punkt innerhalb oder auf der Grenze der Hülle liegt, sonst False.
        """
        for i in range(len(polygon.hull)):
            A = polygon.hull[i]
            B = polygon.hull[(i + 1) % len(polygon.hull)]
            if cross_product(A, B, point) < 0:
                return False
        return True