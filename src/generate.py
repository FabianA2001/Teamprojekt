import shapely.geometry as shap
import random
from CONST import Coord, Edge, Polygon
import CONST
import math
import itertools
import solver


def cross_product(a: Coord, b: Coord, p: Coord) -> float:
    return (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)


def random_coord_global(height: int, width: int) -> Coord:
    OFFSET = int((CONST.OFFSET + CONST.CLUSTER_RADIUS / 2)
                 * CONST.ANTIALIAS_FACTOR)
    return Coord(random.randint(OFFSET, height - OFFSET), random.randint(OFFSET, width - OFFSET))


def random_coord_local(center: Coord, radius: int, form: int) -> Coord:
    if form == 1 or form == 2:
        coord = Coord(random.randint(center.x - radius * 2, center.x + radius * 2),
                      random.randint(center.y - radius, center.y + radius),
                      )
    elif form == 3 or form == 4:
        coord = Coord(random.randint(center.x - radius, center.x + radius),
                      random.randint(center.y - radius * 2,
                                     center.y + radius * 2),
                      )
    elif form == 5:
        coord = Coord(random.randint(center.x - radius * 2, center.x + radius * 2),
                      random.randint(center.y - radius * 2,
                                     center.y + radius * 2),
                      )
    elif form >= 6:
        coord = Coord(random.randint(center.x - radius, center.x + radius),
                      random.randint(center.y - radius, center.y + radius),
                      )
    return coord


def random_cluster(center: Coord, count: int) -> list[Coord]:
    cluster = []
    form = random.randint(1, 10)
    for _ in range(count):
        new_point = random_coord_local(center, CONST.CLUSTER_RADIUS, form)
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
        hull = create_convex_hull(random_cluster(center, CONST.CLUSTER_SIZE))
        polygon = Polygon(hull)
        polygon_list.append(polygon)
    return polygon_list


def create_convex_hull(points: list[Coord]) -> list[Coord]:
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

    start_point = min(points, key=lambda points: (points.x, points.y))
    convex_hull = []
    current_point = start_point
    while True:
        convex_hull.append(current_point)
        next_point = points[0]
        for pot_next_point in points:
            if pot_next_point == current_point:
                continue
            orientation_value = orientation(
                current_point, next_point, pot_next_point)
            if orientation_value == -1 or (orientation_value == 0 and
                                           CONST.calculate_distance(
                                               pot_next_point, current_point)
                                           > CONST.calculate_distance(next_point, current_point)):
                next_point = pot_next_point
        current_point = next_point
        if current_point == start_point:
            break
    return convex_hull


def is_point_inside_polygon(point: Coord, polygon: Polygon) -> bool:
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


def is_polygon_inside_polygon(polygon_in: Polygon, polygon_out: Polygon) -> bool:
    for point in polygon_in.hull:
        if not is_point_inside_polygon(point, polygon_out):
            return False
    return True


def do_polygons_overlap(polygon1: Polygon, polygon2: Polygon) -> bool:
    """
    Überprüft, ob sich zwei Polygone überlappen. (WIP wenn zwei polygone sich kreuzen aber keine punkte ineinander sind)

    :param Polygon polygon1: Das erste zu überprüfende Polygon.
    :param Polygon polygon2: Das zweite zu überprüfende Polygon.

    :return bool: True wenn die Polygone sich überlappen, sonst False.
    """
    for point in polygon1.hull:
        if is_point_inside_polygon(point, polygon2):
            return True
    for point in polygon2.hull:
        if is_point_inside_polygon(point, polygon1):
            return True
    return False


def polygon_intersection(polygon1: Polygon, polygon2: Polygon) -> Polygon | None:
    """
    Berechnet das Polygon, das die Schnittmenge zweier Polygone bildet.

    :param Polygon polygon1: Das erste zu überprüfende Polygon.
    :param Polygon polygon2: Das zweite zu überprüfende Polygon.

    :return Polygon: Das Polygon, das die Schnittmenge darstellt, oder None wenn das Schnittpolygon weniger als 3 Punkte hat.
    """
    edges_polygon1 = CONST.make_edges(polygon1.hull)
    edges_polygon2 = CONST.make_edges(polygon2.hull)
    overlap_points = []
    for i in range(len(edges_polygon1)):
        for j in range(len(edges_polygon2)):
            intersection = edge_intersection(
                edges_polygon1[i], edges_polygon2[j])
            if intersection != None:
                overlap_points.append(intersection)
    for point in polygon1.hull:
        if is_point_inside_polygon(point, polygon2):
            overlap_points.append(point)
    for point in polygon2.hull:
        if is_point_inside_polygon(point, polygon1):
            overlap_points.append(point)
    hull = create_convex_hull(overlap_points)
    if len(hull) > 2:
        polygon = Polygon(hull)
    else:
        return None
    return polygon


def edge_intersection(edge1: Edge, edge2: Edge) -> Coord | None:
    """
    Berechnet den Schnittpunkt von zwei Linien fals vorhanden.

    :param Edge edge1: Die erste Linie.
    :param Edge edge2: Die zweite Linie.

    :return Coord: Der Punkt an dem sich die Lininen Schnieden, oder None wenn sie sich nicht scheiden.
    """
    determinant = ((edge1.point2.x - edge1.point1.x) * (edge2.point2.y - edge2.point1.y)
                   - (edge1.point2.y - edge1.point1.y) *
                   (edge2.point2.x - edge2.point1.x)
                   )
    if determinant == 0:
        return None

    t = (((edge2.point1.x - edge1.point1.x) * (edge2.point2.y - edge2.point1.y)
          - (edge2.point1.y - edge1.point1.y) * (edge2.point2.x - edge2.point1.x)) / determinant
         )
    u = (((edge2.point1.x - edge1.point1.x) * (edge1.point2.y - edge1.point1.y)
          - (edge2.point1.y - edge1.point1.y) * (edge1.point2.x - edge1.point1.x)) / determinant
         )

    if 0 <= t <= 1 and 0 <= u <= 1:
        x = edge1.point1.x + t * (edge1.point2.x - edge1.point1.x)
        y = edge1.point1.y + t * (edge1.point2.y - edge1.point1.y)
        return Coord(round(x), round(y))
    return None


def create_intersecting_polygons(polygon_list: list[Polygon]) -> list[Polygon]:
    """
    Berechnet alle Schnittpolygone zwischen den Polygonen in der gegebenen Liste.

    :param list[Polygon] polygon_list: Die übergebene Liste an Polygonen.

    :return list[Polygon]: Eine Liste mit allen Schnittpolygonen.
    """
    MAX_POSSIBLE_DISTANCE = math.sqrt(
        math.pow(CONST.CLUSTER_RADIUS, 2) + math.pow(CONST.CLUSTER_RADIUS, 2)) * 4
    new_polygon_list = []
    for i in range(len(polygon_list)):
        for j in range(i, len(polygon_list)):
            if i != j and CONST.calculate_distance(polygon_list[i].centroid, polygon_list[j].centroid) <= MAX_POSSIBLE_DISTANCE:
                if do_polygons_overlap(polygon_list[i], polygon_list[j]):
                    intersecting_polygon = polygon_intersection(
                        polygon_list[i], polygon_list[j])
                    if intersecting_polygon != None:
                        new_polygon_list.append(intersecting_polygon)
                    else:
                        new_polygon_list.append(polygon_list[i])
                        new_polygon_list.append(polygon_list[j])
    return new_polygon_list


def find_non_intersecting_polygons(polygon_list: list[Polygon]) -> list[Polygon]:
    """
    Findet alle Polygone in einer Liste, die sich mit keinem anderen Polygon überschneiden.

    :param list[Polygon] polygon_list: Die übergebene Liste an Polygonen.

    :return list[Polygon]: Eine Liste mit allen Polygonen die keine Überschneidungen haben.
    """
    MAX_POSSIBLE_DISTANCE = math.sqrt(
        math.pow(CONST.CLUSTER_RADIUS, 2) + math.pow(CONST.CLUSTER_RADIUS, 2)) * 4
    new_polygon_list = []
    for i in range(len(polygon_list)):
        has_intersection = False
        for j in range(len(polygon_list)):
            if i != j and CONST.calculate_distance(polygon_list[i].centroid, polygon_list[j].centroid) <= MAX_POSSIBLE_DISTANCE:
                if do_polygons_overlap(polygon_list[i], polygon_list[j]):
                    has_intersection = True
        if has_intersection == False:
            new_polygon_list.append(polygon_list[i])
    return new_polygon_list


def is_polygon_covered(polygon: Polygon, test_polygon_list: list[Polygon]) -> bool:
    for test_polygon in test_polygon_list:
        if is_polygon_inside_polygon(test_polygon, polygon):
            return True
    return False


def is_every_polygon_covered(original_polygon_list: list[Polygon], test_polygon_list: list[Polygon]) -> bool:
    for original_polygon in original_polygon_list:
        if is_polygon_covered(original_polygon, test_polygon_list):
            continue
        else:
            return False
    return True


def find_redundant_polygon(original_polygon_list: list[Polygon], current_polygon_list: list[Polygon]) -> Polygon | None:
    for i in range(len(current_polygon_list)):
        test_polygon_list = [elem for elem in current_polygon_list]
        test_polygon_list.pop(i)
        if is_every_polygon_covered(original_polygon_list, test_polygon_list):
            return current_polygon_list[i]
    return None


def remove_redundant_polygons(original_polygon_list: list[Polygon], current_polygon_list: list[Polygon]) -> list[Polygon]:
    while True:
        test_polygon_list = [elem for elem in current_polygon_list]
        redundant_polygon = find_redundant_polygon(
            original_polygon_list, test_polygon_list)
        if redundant_polygon != None:
            print("remove")
            current_polygon_list.remove(redundant_polygon)
        else:
            break
    return current_polygon_list


def is_same_polygon(polygon1: Polygon, polygon2: Polygon) -> bool:
    if -2 <= polygon1.centroid.x - polygon2.centroid.x <= 2 or -2 <= polygon1.centroid.y - polygon2.centroid.y <= 2:
        return True
    return False


def remove_duplicate_polygons(polygon_list: list[Polygon]) -> list[Polygon]:
    no_duplicants_list = []
    for polygon in polygon_list:
        for nd_polygon in no_duplicants_list:
            if is_same_polygon(polygon, nd_polygon):
                break
        no_duplicants_list.append(polygon)
    return no_duplicants_list


def create_better_polygon_list(original_polygon_list: list[Polygon], polygon_list: list[Polygon]) -> list[Polygon]:
    intersecting_polygons = create_intersecting_polygons(polygon_list)
    non_intersecting_polygons = find_non_intersecting_polygons(polygon_list)
    combined_list = intersecting_polygons + non_intersecting_polygons
    new_polygon_list = remove_duplicate_polygons(combined_list)
    return remove_redundant_polygons(original_polygon_list, new_polygon_list)


def find_best_polygon_list(polygon_list: list[Polygon]) -> list[Polygon]:
    current = [elem for elem in polygon_list]
    iteration = 0
    while True:
        new = create_better_polygon_list(polygon_list, current)
        if iteration >= 2:
            if len(new) != len(current):
                current = [elem for elem in new]
            else:
                break
        current = [elem for elem in new]
        iteration += 1
        if len(current) >= 100:
            break
    return current


def find_best_polygon_list_2(own_polygon_list: list[Polygon]) -> list[Polygon]:
    def find_intersection() -> bool:
        for x, y in itertools.combinations(range(len(polygon_list)), 2):
            # Berechne die Schnittmenge
            intersection = polygon_list[x].intersection(polygon_list[y])

            # Prüfen, ob eine Schnittmenge existiert
            if not intersection.is_empty:
                del polygon_list[x]
                if x < y:
                    del polygon_list[y-1]
                else:
                    del polygon_list[y]
                polygon_list.append(intersection)
                return True
        return False

    MAX_INTERATIONS = 300
    polygon_list = []

    for old_poly in own_polygon_list:
        polygon_list.append(shap.Polygon(
            [(coord.x, coord.y) for coord in old_poly.hull]))

    for _ in range(MAX_INTERATIONS):
        if not find_intersection():
            break

    result = []
    for poly in polygon_list:
        hull_coords = list(poly.convex_hull.exterior.coords)
        result.append(
            Polygon([Coord(int(point[0]), int(point[1])) for point in hull_coords[:-1]]))
    return result

# bekommt die aktuelle Tour und die hinzdernisse übergeben
# gibt Tuple aus Coordinaten zurück, zwischen denen sich ein Hinternis befindet


def find_obstacle(tour: list[Coord], obstacles_list: list[Polygon]):
    obstacles = []
    problem_points = []
    for polygon in obstacles_list:
        obstacle = shap.Polygon([(coord.x, coord.y) for coord in polygon.hull])
        obstacles.append(obstacle)
    for i in range(len(tour)-1):
        line = shap.LineString([
            (tour[i].x, tour[i].y), (tour[i+1].x, tour[i+1].y)])
        for obstacle in obstacles:
            if line.intersects(obstacle):
                problem_points.append((tour[i], tour[i+1]))

    return problem_points



def find_obstacle_plus_bypass(tour: list[Coord], obstacles_list: list[Polygon]):
    obstacles = []
    new_tour = tour.copy()
    for polygon in obstacles_list:
        obstacle = shap.Polygon([(coord.x, coord.y) for coord in polygon.hull])
        obstacles.append(obstacle)
    for i in range(len(tour) - 1):
        line = shap.LineString([
            (tour[i].x, tour[i].y), (tour[i + 1].x, tour[i + 1].y)])
        for obstacle in obstacles:
            if line.intersects(obstacle):
                bypass_points = bypass_polygon_for_found_obstacle(obstacle, tour[i], tour[i + 1])
                new_tour = new_tour[:(new_tour.index(tour[i]) + 1)] + bypass_points + new_tour[new_tour.index(tour[i + 1]):]
                break
    return new_tour



def bypass_polygon_for_found_obstacle(polygon: shap.Polygon, start: Coord, end: Coord):
    line = shap.LineString([tuple(start), tuple(end)])
    intersection = polygon.intersection(line)
    assert (not intersection.is_empty)
    assert (intersection.geom_type == 'LineString')
    intersection = list(intersection.coords)

    point1 = shap.Point(intersection[0])
    point2 = shap.Point(intersection[1])
    polygon_exterior = list(polygon.exterior.coords)[:-1]

    def get_tour(point1, point2):
        def get_index(point, liste):
            # Berechne die Entfernungen und finde den nächsten Eckpunkt
            nearest_point = min(
                liste, key=lambda vertex: point.distance(shap.Point(vertex)))
            return liste.index(nearest_point)

        points = polygon_exterior.copy()
        start_index = get_index(point1, points)
        points = points[start_index:] + points[:start_index]
        end_index = get_index(point2, points)
        del points[end_index+1:]

        tour = CONST.to_coord(points)

        if start_index < end_index:
            return tour
        else:
            return list(reversed(tour))

    tour1 = get_tour(point1, point2)
    tour2 = get_tour(point2, point1)

    tour = tour1
    if solver.calculate_tour_distance(tour1) > solver.calculate_tour_distance(tour2):
        tour = tour2

    for _ in range(len(tour)-2):
        if len(tour) <= 2:
            break
        line = shap.LineString([tuple(start), tuple(tour[1])])
        intersection = polygon.intersection(line)
        if intersection.geom_type == 'Point':
            del tour[0]
        else:
            break

    if len(tour) <= 1:
        return tour

    for _ in range(len(tour)-1):
        if len(tour) <= 1:
            break
        line = shap.LineString([tuple(end), tuple(tour[-2])])
        intersection = polygon.intersection(line)
        if intersection.geom_type == 'Point':
            del tour[-1]
        else:
            break

    return tour



def bypass_polygon(old_poly: Polygon, start: Coord, end: Coord):
    polygon = shap.Polygon([(coord.x, coord.y) for coord in old_poly.hull])
    line = shap.LineString([tuple(start), tuple(end)])
    intersection = polygon.intersection(line)
    assert (not intersection.is_empty)
    assert (intersection.geom_type == 'LineString')
    intersection = list(intersection.coords)

    point1 = shap.Point(intersection[0])
    point2 = shap.Point(intersection[1])
    polygon_exterior = list(polygon.exterior.coords)[:-1]

    def get_tour(point1, point2):
        def get_index(point, liste):
            # Berechne die Entfernungen und finde den nächsten Eckpunkt
            nearest_point = min(
                liste, key=lambda vertex: point.distance(shap.Point(vertex)))
            return liste.index(nearest_point)

        points = polygon_exterior.copy()
        start_index = get_index(point1, points)
        points = points[start_index:] + points[:start_index]
        end_index = get_index(point2, points)
        del points[end_index+1:]

        tour = CONST.to_coord(points)

        if start_index < end_index:
            return tour
        else:
            return list(reversed(tour))

    tour1 = get_tour(point1, point2)
    tour2 = get_tour(point2, point1)

    tour = tour1
    if solver.calculate_tour_distance(tour1) > solver.calculate_tour_distance(tour2):
        tour = tour2

    for _ in range(len(tour)-2):
        if len(tour) <= 2:
            break
        line = shap.LineString([tuple(start), tuple(tour[1])])
        intersection = polygon.intersection(line)
        if intersection.geom_type == 'Point':
            del tour[0]
        else:
            break

    if len(tour) <= 1:
        return tour

    for _ in range(len(tour)-1):
        if len(tour) <= 1:
            break
        line = shap.LineString([tuple(end), tuple(tour[-2])])
        intersection = polygon.intersection(line)
        if intersection.geom_type == 'Point':
            del tour[-1]
        else:
            break

    return tour
