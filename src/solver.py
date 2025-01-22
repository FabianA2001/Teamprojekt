from CONST import Coord, Edge, Polygon
import CONST
import math
import gurobipy as gp
from gurobipy import GRB
import generate
import shapely.geometry as shap


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
    angles = [caluculate_angle(path[-2], path[0], path[1])]
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


def gurobi_solver(pointslist: list[list[Coord]], orderlist: list[Coord]):
    env = gp.Env(empty=True)  # Create an environment without startup logs
    # Disable console output for the environment
    env.setParam('LogToConsole', 0)
    env.setParam(GRB.Param.TimeLimit, CONST.GUROBI_MAX_TIME)
    env.start()

    model = gp.Model(env=env)
    # Vars
    vars = {}
    for points in pointslist:
        for point in points:
            vars[point] = model.addVar(vtype=GRB.BINARY)
    # Constraint
    for points in pointslist:
        model.addConstr(sum((vars[point]) for point in points) == 1)

    # Objective
    order: list[list[Coord]] = []
    dist = 0
    for opoint in orderlist:
        for ppoints in pointslist:
            for point in ppoints:
                if opoint.x == point.x and opoint.y == point.y:
                    order.append(ppoints)

    dist = 0
    for i in range(len(order)-1):
        for point1 in order[i]:
            for point2 in order[(i+1) % len(order)]:
                dist += calculate_distance(
                    point1, point2) * vars[point1] * vars[point2]

    model.setObjective(dist, GRB.MINIMIZE)
    model.optimize()
    retpoints = []

    for pointss in order:
        for point in pointss:
            # print("h", vars[point], vars[point].X)
            if vars[point].X > 0.5:
                retpoints.append(point)

    return retpoints


def move_points(polygon_list, points):
    # for point in points:
    # for p, polygon in enumerate(polygon_list):
    #     if generate.is_point_inside_polygon(point, polygon):
    #         print(p)
    polygon_list_neu = []
    points_neu = []
    for point in points:
        points_neu.append(shap.Point(point.x, point.y))

    for old_poly in polygon_list:
        polygon_list_neu.append(shap.Polygon(
            [(coord.x, coord.y) for coord in old_poly.hull]))
    for i in range(1, len(points)-2):
        current_angle = caluculate_angle(
            points[i-1], points[i], points[i+1])
        poly = -1
        for p, polygon in enumerate(polygon_list_neu):
            # print(points[i])
            # print(polygon)
            if (polygon.contains(points_neu[i]) or polygon.boundary.contains(points_neu[i])):
                poly = p
                break

            # if generate.is_point_inside_polygon(points[i], polygon):
            #     poly = p
            #     break
        # print(poly)
        for j in range(3):
            new_points = []
            new_points.append(points[i])
            k = 0
            while k < 5:
                new_point = generate.random_coord_local(
                    points[i], 500-(100*j), 6)
                # if generate.is_point_inside_polygon(new_point, polygon_list[poly],):
                #     new_points.append(new_point)
                #     k += 1
                if polygon_list_neu[poly].contains(shap.Point(new_point.x, new_point.y)) or polygon_list_neu[poly].boundary.contains(shap.Point(new_point.x, new_point.y)):
                    new_points.append(new_point)
                    k += 1
            for point in new_points:
                new_angle = caluculate_angle(
                    points[i-1], point, points[i+1])
                if new_angle < current_angle:
                    current_angle = new_angle
                    points[i] = point
    # for point in points:
    #     for p, polygon in enumerate(polygon_list):
    #         if generate.is_point_inside_polygon(polygon, point):
    #             print(p)

    return points


def find_obstacle(tour: list[Coord], obstacles_list: list[Polygon]):
    """
    bekommt die aktuelle Tour und die hindernisse übergeben
    gibt Tuple aus Coordinaten zurück, zwischen denen sich ein Hinternis befindet
    """
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
    if calculate_tour_distance(tour1) > calculate_tour_distance(tour2):
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