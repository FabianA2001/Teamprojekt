from reconnect_folder import reconnect_classes as rclass
import math
import random



def get_distance(point0, point1):
    return math.sqrt((point0.x - point1.x) ** 2 + (point0.y - point1.y) ** 2)


def caluculate_angle(p1, p2, p3):
    assert ((p1 != p2) and (p1 != p3) and (p2 != p3))
    vec_a = (p2.x - p1.x, p2.y - p1.y)
    vec_b = (p3.x - p2.x, p3.y - p2.y)
    mag_a = math.sqrt(vec_a[0] ** 2 + vec_a[1] ** 2)
    mag_b = math.sqrt(vec_b[0] ** 2 + vec_b[1] ** 2)
    assert (mag_a != 0 and mag_b != 0)
    dot_product = vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]
    cos_theta = dot_product / (mag_a * mag_b)
    cos_theta = max(-1, min(1, cos_theta))
    return math.acos(cos_theta) * (180 / math.pi)


def get_angle(edges_of_point):
    sum_angles = 0
    for i in range(len(edges_of_point)):
        for j in range(i):
            if edges_of_point[i].points[0] == edges_of_point[j].points[0]:
                sum_angles += caluculate_angle(edges_of_point[i].points[1], edges_of_point[i].points[0], edges_of_point[j].points[1]) * edges_of_point[i].var * edges_of_point[j].var
            elif edges_of_point[i].points[0] == edges_of_point[j].points[1]:
                sum_angles += caluculate_angle(edges_of_point[i].points[1], edges_of_point[i].points[0], edges_of_point[j].points[0]) * edges_of_point[i].var * edges_of_point[j].var
            elif edges_of_point[i].points[1] == edges_of_point[j].points[0]:
                sum_angles += caluculate_angle(edges_of_point[i].points[0], edges_of_point[i].points[1], edges_of_point[j].points[1]) * edges_of_point[i].var * edges_of_point[j].var
            else:
                sum_angles += caluculate_angle(edges_of_point[i].points[0], edges_of_point[i].points[1], edges_of_point[j].points[0]) * edges_of_point[i].var * edges_of_point[j].var
    return sum_angles


def get_angels_distance(tour):
    angles = caluculate_angle(tour[-2], tour[0], tour[1])
    for i in range(1, len(tour) - 1):
        angles += caluculate_angle(tour[i - 1], tour[i], tour[i + 1])
    distance = 0
    for i in range(len(tour) - 1):
        distance += get_distance(tour[i], tour[i + 1])
    return angles, distance


'''----------------'''


def get_random_tour(num):
    tour = []
    for _ in range(num):
        tour.append(rclass.Point(random.randint(0, 10000), random.randint(0, 10000)))
    return tour


def get_random_center(tour):
    return tour[random.randint(0, len(tour) - 1)]


def sort_tour(tour, center):
    return sorted(tour, key=lambda point : get_distance(point, center))


'''----------------'''


def get_red_blue_points(tour, sorted_by_distance, max_colored_points):
    red_points = [sorted_by_distance[0]]
    blue_points = [tour[tour.index(sorted_by_distance[0]) - 1], tour[(tour.index(sorted_by_distance[0]) + 1) % len(tour)]]
    old_red_points = []
    old_blue_points = []
    index = 1
    if len(tour) <= max_colored_points - 1:
        red_points = tour.copy()
        blue_points = []
        return red_points, blue_points
    while len(red_points) + len(blue_points) <= max_colored_points:
        if index == len(tour):
            break
        old_red_points = red_points.copy()
        old_blue_points = blue_points.copy()
        red_points.append(sorted_by_distance[index])
        index += 1
        blue_points = []
        for i in range(len(tour)):
            if tour[i] not in red_points:
                if tour[i - 1] in red_points or tour [(i + 1) % len(tour)] in red_points:
                    blue_points.append(tour[i])
    red_points =  old_red_points.copy()
    blue_points = old_blue_points.copy()
    for i in range(len(tour)):
        if tour[i] in blue_points:
            if tour[i - 1] in red_points and tour[(i + 1) % len(tour)] in red_points:
                blue_points.remove(tour[i])
                red_points.append(tour[i])
    return red_points, blue_points


def get_colored_points(red_points, blue_points):
    colored_points = red_points.copy()
    colored_points.extend(blue_points)
    return colored_points


def get_powerset(red_points):
    powerset_points = [[]]
    for point in red_points:
        length = len(powerset_points)
        for i in range(length):
            subset = powerset_points[i].copy()
            subset.append(point)
            powerset_points.append(subset)
    return powerset_points


def get_list_of_blue_pairs(tour, red_points, blue_points):
    list_of_blue_pairs = []
    if len(red_points) != len(tour):
        i = 0
        while tour[i] not in red_points:
            i -= 1
        while tour[i % len(tour)] in red_points:
            i += 1
        j = 0
        while j < len(tour):
            if tour[(i + j) % len(tour)] in blue_points:
                two_list = [tour[(i + j) % len(tour)]]
                j += 1
                while tour[(i + j) % len(tour)] not in blue_points:
                    j += 1
                two_list.append(tour[(i + j) % len(tour)])
                list_of_blue_pairs.append(two_list)
            j += 1
    return list_of_blue_pairs


'''----------------'''


def get_blue_edges(tour, blue_points, colored_points, m):
    blue_edges = []
    for i in range(len(tour)):
        if tour[i] in blue_points:
            if tour[i - 1] not in colored_points:
                blue_edges.append(rclass.Edge([tour[i], tour[i - 1]], m))
            elif tour[(i + 1) % len(tour)] not in colored_points:
                blue_edges.append(rclass.Edge([tour[i], tour[(i + 1) % len(tour)]], m))
            elif tour[i - 1] in blue_edges:
                blue_edges.append(rclass.Edge([tour[i], tour[i - 1]], m))
    return blue_edges


def get_virtual_edges(list_of_blue_pairs, m):
    virtual_edges = []
    for edge_of_two_blue in list_of_blue_pairs:
        virtual_edges.append(rclass.Edge([edge_of_two_blue[0], edge_of_two_blue[1]], m))
    return virtual_edges


def get_real_edges(colored_points, list_of_blue_pairs, m):
    real_edges = []
    for i in range(len(colored_points)):
        for j in range(i):
            if [colored_points[i], colored_points[j]] not in list_of_blue_pairs and [colored_points[j], colored_points[i]] not in list_of_blue_pairs:
                real_edges.append(rclass.Edge([colored_points[i], colored_points[j]], m))
    return real_edges


def get_edges(real_edges, virtual_edges):
    edges = real_edges.copy()
    edges.extend(virtual_edges)
    return edges


def get_real_edges_with_blue(real_edges, blue_edges):
    real_edges_with_blue = real_edges.copy()
    real_edges_with_blue.extend(blue_edges)
    return real_edges_with_blue


'''----------------'''


def get_important_edges(real_edges, red_points, tour, blue_points, m):
    important_edges = []
    for edge in real_edges:
        if edge.var.X == 1:
            important_edges.append(edge)
    if len(red_points) != len(tour):
        i = 0
        while tour[i] not in red_points:
            i -= 1
        while tour[i % len(tour)] in red_points:
            i += 1
        j = 0
        while j < len(tour):
            if tour[(i + j) % len(tour)] in blue_points:
                while tour[(i + j + 1) % len(tour)] not in red_points:
                    important_edges.append(rclass.Edge([tour[(i + j) % len(tour)], tour[(i + j + 1) % len(tour)]], m))
                    j += 1
            j += 1
    return important_edges


def get_new_tour(real_edges, red_points, tour, blue_points, m):
    important_edges = get_important_edges(real_edges, red_points, tour, blue_points, m)
    new_tour = []
    new_tour.append(important_edges[0].points[0])
    new_tour.append(important_edges[0].points[1])
    for _ in range(len(important_edges) - 1):
        for important_edge in important_edges:
            if important_edge.points[0] == new_tour[-1] and important_edge.points[1] != new_tour[-2]:
                new_tour.append(important_edge.points[1])
                break
            elif important_edge.points[1] == new_tour[-1] and important_edge.points[0] != new_tour[-2]:
                new_tour.append(important_edge.points[0])
                break
    return new_tour


'''----------------'''


def is_opt_angle_best_tour(opt_angles_angles, opt_angles_distance, opt_distance_angles, opt_distance_distance, opt_ratio_angles, opt_ratio_distance):
    if opt_angles_angles <= opt_distance_angles and opt_angles_angles <= opt_ratio_angles:
        if opt_angles_distance <= opt_distance_distance and opt_angles_distance <= opt_ratio_distance:
            return True
    return False


def is_opt_distance_best_tour(opt_angles_angles, opt_angles_distance, opt_distance_angles, opt_distance_distance, opt_ratio_angles, opt_ratio_distance):
    if opt_distance_angles <= opt_angles_angles and opt_distance_angles <= opt_ratio_angles:
        if opt_distance_distance <= opt_angles_distance and opt_distance_distance <= opt_ratio_distance:
            return True
    return False
