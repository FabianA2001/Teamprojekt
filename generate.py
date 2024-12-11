import random
from CONST import Coord
import math
import CONST


def calculate_distance(point1: Coord, point2: Coord) -> float:
    distance = math.sqrt(
        math.pow((point1.x - point2.x), 2) +
        math.pow((point1.y - point2.y), 2)
    )
    return distance


def is_enough_distance(coord1: Coord, coord2: Coord, distance: int) -> bool:
    if calculate_distance(coord1, coord2) >= distance:
        return True
    return False


def generate_areas(count: int, height: int, width: int) -> list[list[Coord]]:
    """
    Generiert zufällige Positionen, an denen mit "generate_cluster()" ein Punkte-Cluster erzeugt wird.
    
    :param int count: Die Anzahl an Clustern die insgesamt generiert werden sollen.
    :param int height: Die Höhe des Bereiches in dem die Positionen generiert werden können.
    :param int width: Die Breite des Bereiches in dem die Positionen generiert werden können.
    
    :return list[list[Coord]]: Eine zweidimensonale Liste mit Koordinaten, wobei jede Zeile einem Punkte-Cluster entspricht.
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
                    continue    # Beim ersten Punkt wird nicht verglichen, um das Vergleichen mit einer leeren Liste zuverhindern.
                if is_enough_distance(area_location, location, CONST.MIN_DISTANCE_AREA):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster = generate_cluster(CONST.CLUSTER_SIZE, area_location)
                areas_list.append(cluster)
                break
    return areas_list
          

def generate_cluster(count: int, center: Coord) -> list[Coord]:
    """
    Generiert ein Punkte-Cluster in einem Radius um einen übergebenen Punkt.

    :param int count: Die Anzahl an Punkten die ein Cluster enthält.
    :param Coord center: Die Koordinaten des Mittelpunktes des Cluster ("center" ist selbst kein Punkt im Cluster).

    return list[Coord]: Eine Liste die die Koordinaten der Punkte im Cluster enthält.
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
                    continue    # Beim ersten Punkt wird nicht verglichen, um das Vergleichen mit einer leeren Liste zuverhindern.
                if is_enough_distance(cluster_point, point, CONST.MIN_DISTANCE_CLUSTER):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster_list.append(cluster_point)
                break
    return cluster_list