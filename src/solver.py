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

        angle = caluculate_angle(p1, p2, p3)

        if p1.x == p2.x and p1.y == p2.y:
            angle = caluculate_angle(path[i - 2], p2, p3)

        angles.append(angle)
    return angles


def calculate_dis_angle(points: list[Coord]):
    return calculate_tour_distance(points), sum(calculate_turn_angles(points))


def caluculate_angle(p1, p2, p3):
    # Berechne die Vektoren zwischen den Punkten
    vec_a = (p2.x - p1.x, p2.y - p1.y)
    vec_b = (p3.x - p2.x, p3.y - p2.y)

    # Berechne die Länge der Vektoren
    mag_a = math.sqrt(vec_a[0] ** 2 + vec_a[1] ** 2)
    mag_b = math.sqrt(vec_b[0] ** 2 + vec_b[1] ** 2)

    if mag_a == 0 or mag_b == 0:
        return 0

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
                if new_angle <= current_angle-1:
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
                other_obstacles = obstacles.copy()
                other_obstacles.remove(obstacle)
                bypass_points = bypass_polygon_for_found_obstacle(
                    obstacle, tour[i], tour[i + 1], other_obstacles)
                if bypass_points == None:
                    break
                bypass_points = CONST.to_coord(bypass_points)
                new_tour = new_tour[:(new_tour.index(
                    tour[i]) + 1)] + bypass_points + new_tour[new_tour.index(tour[i + 1]):]
                break
    return new_tour


def bypass_polygon_for_found_obstacle(polygon: shap.Polygon, start: Coord, end: Coord, other_obstacles: list[shap.Polygon]):
    line = shap.LineString([tuple(start), tuple(end)])
    intersection = polygon.intersection(line)
    assert (not intersection.is_empty)
    assert (intersection.geom_type == 'LineString')

    if polygon.contains(shap.Point(start.x, start.y)) or polygon.contains(shap.Point(end.x, end.y)):
        return None

    intersection = list(intersection.coords)
    point1 = intersection[0]
    point2 = intersection[1]

    if calculate_distance(start, Coord(point2[0], point2[1])) < calculate_distance(start, Coord(point1[0], point1[1])):
        point1, point2 = point2, point1

    vertices = list(polygon.exterior.coords)[:-1]

    edges_of_polygon = [shap.LineString(
        [vertices[i - 1], vertices[i]]) for i in range(len(vertices))]

    tour_up_first = None
    tour_up_last = None
    tour_down_first = None
    tour_down_last = None

    for edge in edges_of_polygon:
        inter = edge.intersection(line)
        if not inter.is_empty:
            if inter.coords[0] == intersection[0]:
                tour_up_first = edge.coords[1]
                tour_down_first = edge.coords[0]
            elif inter.coords[0] == intersection[1]:
                tour_up_last = edge.coords[0]
                tour_down_last = edge.coords[1]

    if tour_up_first == None or tour_up_last == None:
        return None
    if tour_down_first == None or tour_down_last == None:
        return None

    tour_up = []
    first_up_index = vertices.index(tour_up_first)
    for i in range(len(vertices)):
        tour_up.append(vertices[(first_up_index + i) % len(vertices)])
        if vertices[(first_up_index + i) % len(vertices)] == tour_up_last:
            break

    tour_down = []
    first_down_index = vertices.index(tour_down_first)
    for i in range(len(vertices)):
        tour_down.append(vertices[first_down_index - i])
        if vertices[first_down_index - i] == tour_down_last:
            break

    '''delete useless points'''
    while True:
        if len(tour_up) <= 1:
            break
        start_line = shap.LineString([tuple(start), tour_up[1]])
        inter = polygon.intersection(start_line)
        if inter.geom_type == 'Point':
            del tour_up[0]
        else:
            break

    while True:
        if len(tour_up) <= 1:
            break
        end_line = shap.LineString([tuple(end), tour_up[-2]])
        inter = polygon.intersection(end_line)
        if inter.geom_type == 'Point':
            del tour_up[-1]
        else:
            break

    while True:
        if len(tour_down) <= 1:
            break
        start_line = shap.LineString([tuple(start), tour_down[1]])
        inter = polygon.intersection(start_line)
        if inter.geom_type == 'Point':
            del tour_down[0]
        else:
            break

    while True:
        if len(tour_down) <= 1:
            break
        end_line = shap.LineString([tuple(end), tour_down[-2]])
        inter = polygon.intersection(end_line)
        if inter.geom_type == 'Point':
            del tour_down[-1]
        else:
            break

    '''check if another polygon is in between'''
    line_start_up = shap.LineString([tuple(start), tour_up[0]])
    for obstacle in other_obstacles:
        if obstacle.intersects(line_start_up):
            new_other_obstacles = other_obstacles.copy()
            new_other_obstacles.remove(obstacle)
            bypass_points = bypass_polygon_for_found_obstacle(
                obstacle, start, Coord(tour_up[0][0], tour_up[0][1]), new_other_obstacles)
            if bypass_points == None:
                break
            tour_up = bypass_points + tour_up
            break
    del line_start_up

    line_end_up = shap.LineString([tour_up[-1], end])
    for obstacle in other_obstacles:
        if obstacle.intersects(line_end_up):
            new_other_obstacles = other_obstacles.copy()
            new_other_obstacles.remove(obstacle)
            bypass_points = bypass_polygon_for_found_obstacle(obstacle, Coord(
                tour_up[-1][0], tour_up[-1][1]), end, new_other_obstacles)
            if bypass_points == None:
                break
            tour_down = tour_up + bypass_points
            break
    del line_end_up

    line_start_down = shap.LineString([tuple(start), tour_down[0]])
    for obstacle in other_obstacles:
        if obstacle.intersects(line_start_down):
            new_other_obstacles = other_obstacles.copy()
            new_other_obstacles.remove(obstacle)
            bypass_points = bypass_polygon_for_found_obstacle(
                obstacle, start, Coord(tour_down[0][0], tour_down[0][1]), new_other_obstacles)
            if bypass_points == None:
                break
            tour_down = bypass_points + tour_down
            break
    del line_start_down

    line_end_down = shap.LineString([tour_down[-1], end])
    for obstacle in other_obstacles:
        if obstacle.intersects(line_end_down):
            new_other_obstacles = other_obstacles.copy()
            new_other_obstacles.remove(obstacle)
            bypass_points = bypass_polygon_for_found_obstacle(obstacle, Coord(
                tour_down[-1][0], tour_down[-1][1]), end, new_other_obstacles)
            if bypass_points == None:
                break
            tour_down = tour_down + bypass_points
            break
    del line_end_down

    '''check which tour is better'''
    tour_up_with_start_end = [tuple(start)]
    for point in tour_up:
        tour_up_with_start_end.append(point)
    tour_up_with_start_end.append(tuple(end))

    tour_down_with_start_end = [tuple(start)]
    for point in tour_down:
        tour_down_with_start_end.append(point)
    tour_down_with_start_end.append(tuple(end))

    sum_up = 0
    for i in range(len(tour_up_with_start_end) - 1):
        sum_up += calculate_distance(Coord(tour_up_with_start_end[i][0], tour_up_with_start_end[i][1]),
                                     Coord(tour_up_with_start_end[i + 1][0], tour_up_with_start_end[i + 1][1]))

    sum_down = 0
    for i in range(len(tour_down_with_start_end) - 1):
        sum_down += calculate_distance(Coord(tour_down_with_start_end[i][0], tour_down_with_start_end[i][1]),
                                       Coord(tour_down_with_start_end[i + 1][0], tour_down_with_start_end[i + 1][1]))

    tour = tour_up
    if sum_down < sum_up:
        tour = tour_down

    return tour


def change_point_in_obstacle(tour: list[Coord], obstacles_list: list[Polygon], polygon_list: list[Polygon]):
    obstacles = []
    polygons = []
    for polygon in obstacles_list:
        obstacle = shap.Polygon([(coord.x, coord.y) for coord in polygon.hull])
        obstacles.append(obstacle)
    points = []
    for polygon in polygon_list:
        polygonn = shap.Polygon([(coord.x, coord.y) for coord in polygon.hull])
        polygons.append(polygonn)
    for j, point in enumerate(tour):
        for obstacle in obstacles:
            if obstacle.contains(shap.Point(point.x, point.y)) or obstacle.boundary.contains(shap.Point(point.x, point.y)):
                for i, polygon in enumerate(polygons):
                    if polygon.contains(shap.Point(point.x, point.y)) or polygon.boundary.contains(shap.Point(point.x, point.y)):
                        poly = i
                        break
                points = []
                res = []
                l = 1
                loop = 1
                while (loop):
                    for k in range(10):
                        # print("loop")
                        point1 = generate.random_coord_local(point, 100*l, 6)
                        # while obstacle.contains(shap.Point(point1.x, point1.y)) or obstacle.boundary.contains(shap.Point(point1.x, point1.y)):
                        # point1 = random_coord_local(point, 100*l, 6)
                        points.append(point1)

                    for p, point in enumerate(points):
                        if not (polygons[poly].contains(shap.Point(point.x, point.y)) or polygons[poly].boundary.contains(shap.Point(point.x, point.y))):
                            # points.pop(p)
                            kom = 0
                        elif obstacle.contains(shap.Point(point.x, point.y)) or obstacle.boundary.contains(shap.Point(point.x, point.y)):
                            # points.pop(p)
                            kom = 1
                        else:
                            res.append(point)

                    if l >= 5:
                        for pointt in list(polygons[poly].exterior.coords):
                            if (not obstacle.contains(shap.Point(pointt[0], pointt[1]))) and (not obstacle.boundary.contains(shap.Point(pointt[0], pointt[1]))):
                                res.append(Coord(pointt[0], pointt[1]))
                    if res == []:
                        l += 1
                        # print("no change")
                    else:
                        # print("change")
                        loop = 0
                # break
        if points != []:
            # print("change happened")
            tour[j] = res[0]
            points = []
            res = []

    return tour


def delete_possible_points(tour, polygons, obstacles):
    polygons = [shap.Polygon([(coord.x, coord.y)
                             for coord in polygon.hull]) for polygon in polygons]
    obstacles = [shap.Polygon([(coord.x, coord.y)
                              for coord in obstacle.hull]) for obstacle in obstacles]
    points = tour.copy()[:-1]
    lines = [shap.LineString([points[i - 1], points[i]])
             for i in range(len(points))]
    while True:
        for point in points:
            point_index = points.index(point)
            line_without_point = shap.LineString(
                [points[point_index - 1], points[(point_index + 1) % len(points)]])
            for obstacle in obstacles:
                inter = obstacle.intersection(line_without_point)
                if not inter.is_empty and inter.geom_type != 'Point':
                    break
            else:
                tour_without_point = points.copy()
                tour_without_point.remove(point)
                lines = [shap.LineString([tour_without_point[i - 1], tour_without_point[i]])
                         for i in range(len(tour_without_point))]
                for polygon in polygons:
                    for line in lines:
                        if polygon.distance(line) < 1:
                            break
                    else:
                        break
                else:
                    points.remove(point)
                    break
        else:
            break
    points.append(points[0])
    return points
