import random
from CONST import Coord, Polygon
import CONST



def is_enough_distance(coord1: Coord, coord2: Coord, distance: int) -> bool:
    if CONST.calculate_distance(coord1, coord2) >= distance:
        return True
    return False

def cross_product(a: Coord, b:Coord, p:Coord) -> float:
    return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)
    


def generate_polygons(count: int, height: int, width: int) -> list[Polygon]:
    """
    Generiert zufällige Positionen, an denen mit "generate_cluster()" ein Punkte-Cluster erzeugt wird.
    
    :param int count: Die Anzahl an Clustern die insgesamt generiert werden sollen.
    :param int height: Die Höhe des Bereiches in dem die Positionen generiert werden können.
    :param int width: Die Breite des Bereiches in dem die Positionen generiert werden können.
    
    :return list[Polygon]: Eine Liste mit Polygon
    """
    OFFSET = (CONST.OFFSET + CONST.CLUSTER_RADIUS) * CONST.ANTIALIAS_FACTOR
    areas_list = []
    verifier = True

    for _ in range(count):
        for attempt in range(100):
            area_location = Coord(
                random.randint(OFFSET, height - OFFSET),
                random.randint(OFFSET, width - OFFSET),
            )
            for location in areas_list:
                if attempt == 0:
                    continue    #Beim ersten Punkt wird nicht verglichen, um das Vergleichen mit einer leeren Liste zuverhindern.
                if is_enough_distance(area_location, location, CONST.MIN_DISTANCE_AREA):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster = generate_cluster(CONST.CLUSTER_SIZE, area_location)
                convexe_hull = create_convexe_hull(cluster)
                polygon = Polygon(convexe_hull)
                areas_list.append(polygon)
                break
    return areas_list
          

def generate_cluster(count: int, center: Coord) -> list[Coord]:
    """
    Generiert ein Punkte-Cluster in einem Radius um einen übergebenen Punkt.

    :param int count: Die Anzahl an Punkten die ein Cluster enthält.
    :param Coord center: Die Koordinaten des Mittelpunktes des Cluster ("center" ist selbst kein Punkt im Cluster).

    :return list[Coord]: Eine Liste die die Koordinaten der Punkte im Cluster enthält.
    """
    cluster_list = []
    verifier = True

    for _ in range(count):
        for attempt in range(100):
            cluster_point = Coord(
                random.randint(center.x - CONST.CLUSTER_RADIUS, center.x + CONST.CLUSTER_RADIUS),
                random.randint(center.y - CONST.CLUSTER_RADIUS, center.y + CONST.CLUSTER_RADIUS),
            )
            for point in cluster_list:
                if attempt == 0:
                    continue    #Beim ersten Punkt wird nicht verglichen, um das Vergleichen mit einer leeren Liste zuverhindern.
                if is_enough_distance(cluster_point, point, CONST.MIN_DISTANCE_CLUSTER):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster_list.append(cluster_point)
                break
    return cluster_list

def create_convexe_hull(points: list[Coord]) -> list[Coord]:
    """
    Findet die konvexe Hülle einer Punktmenge mit dem Jarvis-March-Algorithmus.

    param list[Coord] points: Das Cluster von Punkten für welche die konvexe Hülle generiert werden soll.

    return list[Coord]: Die Liste mit Koordinaten, die die konvexe Hülle bilden.
    """

    def orientation(current_point: Coord, next_point: Coord, pot_next_point: Coord) -> int:
        """
        Gibt die Orientierung von "pot_next_point" zu "next_point" relativ zu "current_point" an.

        param Coord current_point: Der aktuelle Punkt der konvexen Hülle.
        param Coord next_point: Der nächste Punkte der zur konvexen Hülle hinzugefügt werden soll.
        param Coord pot_next_point: potenzielle Punkte die als nächstes hinzugefügt werden könnten.

        return int: die Orientierung der Punkte als integer: -1 -> im Uhrzeigersinn, 0 -> kollinear, 1 -> gegen den Uhrzeigersinn    
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