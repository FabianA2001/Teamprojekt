from CONST import Coord, Edge
import CONST
import math


def solver(points: list[Coord], opt) -> list[Edge]:
    result = []
    # result.append(Edge(Coord(100, 100), Coord(200, 200),))
    coords = farthest_insertion(points, opt)
    for i in range(len(coords)):
        result.append(Edge(coords[i], coords[(i + 1) % len(coords)]))

    return result


def two_opt(tour: list[Coord]) -> list[Coord]:
    tour = tour[0:-1]
    improvement_found = True
    count = 0
    while improvement_found:
        improvement_found = False
        for i in range(len(tour) - 1):
            for j in range(i + 2, len(tour)-2):
                if j == len(tour) - 1 and i == 0:
                    continue  # Vermeiden Sie den Austausch von Start- und Endpunkt

                # Berechnen Sie die aktuelle Turn-Kosten für i, i+1, j und j+1
                current_cost = calculate_distance(tour[i], tour[i+1]) +\
                    calculate_distance(tour[j], tour[j+1]) +\
                    caluculate_angel(tour[i], tour[i+1], tour[i+2]) +\
                    caluculate_angel(tour[j], tour[j+1], tour[j+2])

                # Berechnen Sie die neuen Kosten nach dem Austausch
                new_cost = calculate_distance(tour[i], tour[j]) + \
                    calculate_distance(tour[i+1], tour[j+1]) + \
                    caluculate_angel(tour[i], tour[j+1], tour[i+2]) +\
                    caluculate_angel(tour[j], tour[i+1], tour[j+2])

                # calculate_turn_cost(tour[i], tour[j], tour[i+1], tour[j+1])

                # Überprüfen Sie, ob der Tausch die Kosten reduziert
                if new_cost < current_cost:
                    # Wenn ja, aktualisieren Sie die Tour und setzen das Flag
                    tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    count += 1
                    improvement_found = True
    print("Anzahl der Veränderungen", count)
    tour.append(tour[0])
    return tour


def calculate_distance(point1: Coord, point2: Coord):
    """Berechnet die euklidische Distanz zwischen zwei Punkten."""
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def farthest_insertion(points, opt) -> list[Edge]:
    """
    Implementiert den Farthest Insertion Algorithmus zur Lösung des TSP-Problems.

    :param points: Eine Liste von 2D-Koordinaten (z.B. [(x1, y1), (x2, y2), ...]).
    :return: Eine Liste der Indizes, die die Reihenfolge der Rundreise darstellen.
    """
    # Anzahl der Punkte
    n = len(points)

    # Distanzmatrix vorbereiten (für schnelle Zugriffe auf Distanzen)
    distance_matrix = [
        [calculate_distance(i, j) for j in points] for i in points]

    # 1. Starte mit den beiden am weitesten entfernten Knoten
    max_dist = 0
    start_pair = ((), ())
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if distance_matrix[i][j] > max_dist:
                max_dist = distance_matrix[i][j]
                start_pair = (points[i], points[j])
    # Initialisiere die Tour mit den beiden am weitesten entfernten Knoten
    tour = [start_pair[0], start_pair[1], start_pair[0]]
    # Liste der restlichen Knoten
    unvisited = set(points)
    unvisited.remove(start_pair[0])
    unvisited.remove(start_pair[1])

    # 2. Wiederhole, bis alle Knoten in der Tour enthalten sind
    while unvisited:
        # Finde den am weitesten entfernten Knoten von der aktuellen Tour
        farthest_node = None
        max_dist_to_tour = -1

        for node in unvisited:
            min_dist_to_tour = min(
                distance_matrix[points.index(node)][points.index(tour_node)]
                for tour_node in tour
            )
            if min_dist_to_tour > max_dist_to_tour:
                max_dist_to_tour = min_dist_to_tour
                farthest_node = node

        # Finde die beste Position, um den Knoten in die Tour einzufügen
        best_position = 0
        best_increase = float("inf")

        for i in range(len(tour) - 1):
            current_increase = (
                distance_matrix[points.index(
                    tour[i])][points.index(farthest_node)]
                + distance_matrix[points.index(farthest_node)][
                    points.index(tour[i + 1])
                ]
                - distance_matrix[points.index(tour[i])][points.index(tour[i + 1])]
            )

            if current_increase < best_increase:
                best_increase = current_increase
                best_position = i

        # Füge den Knoten in die beste Position ein
        tour.insert(best_position + 1, farthest_node)

        # Markiere den Knoten als besucht
        unvisited.remove(farthest_node)
    if opt:
        tour = two_opt(tour)

    for i in range(len(tour)):
        edges.append(
            Edge(
                tour[i],
                tour[(i + 1) % len(tour)],
                calculate_distance(tour[i], tour[(i + 1) % len(tour)]),
            )
        )
    summ = 0
    for edge in edges:
        summ += edge.length
    print("Gesamtlänge der Tour: ", summ)

    # Berechne die Abbiegewinkel für den Pfad
    turn_angles = calculate_turn_angles(tour)
    summ = 0
    for i, angle in enumerate(turn_angles):
        # print(f"an Winkel {i+1}: {round(angle, 2)}°")
        summ += angle
    print("anzahl Winkel:", len(turn_angles))
    print("tour:", len(tour))
    print("Gesamtwinkel: ", summ)
    return tour


def calculate_turn_angles(path):
    angles = []
    for i in range(1, len(path) - 1):
        # Hole Koordinaten der drei aufeinanderfolgenden Punkte
        p1, p2, p3 = path[i - 1], path[i], path[i + 1]

        angles.append(caluculate_angel(p1, p2, p3))
    return angles


def caluculate_angel(p1, p2, p3):
    assert ((p1 != p2) and (p1 != p3) and (p2 != p3))
    # Berechne die Vektoren zwischen den Punkten
    vec_a = (p2.x - p1.x, p2.y - p1.y)
    vec_b = (p3.x - p2.x, p3.y - p2.y)

    # Berechne die Länge der Vektoren
    mag_a = math.sqrt(vec_a[0] ** 2 + vec_a[1] ** 2)
    mag_b = math.sqrt(vec_b[0] ** 2 + vec_b[1] ** 2)

    # Berechne den Winkel zwischen den Vektoren
    dot_product = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]
    cos_theta = dot_product / (mag_a * mag_b)

    # Begrenze cos_theta auf den Bereich [-1, 1] um Rundungsfehler zu vermeiden
    cos_theta = max(-1, min(1, cos_theta))

    # Berechne den Winkel in Radiant und konvertiere zu Grad
    return math.acos(cos_theta) * (180 / math.pi)
