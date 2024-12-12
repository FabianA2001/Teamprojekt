from CONST import Coord, Edge
import math


def make_edges(points: list[Coord]) -> list[Edge]:
    result = []
    for i in range(len(points)):
        result.append(Edge(points[i], points[(i + 1) % len(points)]))

    return result


def calculate_distance(point1: Coord, point2: Coord):
    """Berechnet die euklidische Distanz zwischen zwei Punkten."""
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def calculate_tour_distance(tour: list[Coord]):
    summ = 0
    for i, t in enumerate(tour):
        summ += calculate_distance(t, tour[(i+1) % len(tour)])
    return summ


def calculate_turn_angles(path):
    angles = []
    for i in range(1, len(path) - 1):
        # Hole Koordinaten der drei aufeinanderfolgenden Punkte
        p1, p2, p3 = path[i - 1], path[i], path[i + 1]

        angles.append(caluculate_angle(p1, p2, p3))
    return angles


def calculate_dis_angle(points: list[Coord]):
    return calculate_tour_distance(points), sum(calculate_turn_angles(points))


def caluculate_angle(p1, p2, p3):
    assert ((p1 != p2) and (p1 != p3) and (p2 != p3))
    # Berechne die Vektoren zwischen den Punkten
    vec_a = (p2.x - p1.x, p2.y - p1.y)
    vec_b = (p3.x - p2.x, p3.y - p2.y)

    # Berechne die Länge der Vektoren
    mag_a = math.sqrt(vec_a[0] ** 2 + vec_a[1] ** 2)
    mag_b = math.sqrt(vec_b[0] ** 2 + vec_b[1] ** 2)

    assert (mag_a != 0 and mag_b != 0)

    # Berechne den Winkel zwischen den Vektoren
    dot_product = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]
    cos_theta = dot_product / (mag_a * mag_b)

    # Begrenze cos_theta auf den Bereich [-1, 1] um Rundungsfehler zu vermeiden
    cos_theta = max(-1, min(1, cos_theta))

    # Berechne den Winkel in Radiant und konvertiere zu Grad
    return math.acos(cos_theta) * (180 / math.pi)
