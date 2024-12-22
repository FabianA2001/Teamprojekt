from gurobipy import *
import random
import math


m = Model("Optimum")


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


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Edge:
    def __init__(self, points):
        self.points = points
        self.distance = get_distance(points[0], points[1])
        self.var = m.addVar(vtype=GRB.BINARY)


points = []
for i in range(12):
    points.append(Point(random.randint(0, 10000), random.randint(0, 10000)))

powerset_points = [[]]
for point in points:
    length = len(powerset_points)
    for i in range(length):
        subset = powerset_points[i].copy()
        subset.append(point)
        powerset_points.append(subset)

edges = []
for i in range(len(points)):
    for j in range(i):
        edges.append(Edge([points[i], points[j]]))

bool_angles = True
if bool_angles:
    '''Min Angles'''
    m.setObjective(quicksum(get_angle([edge for edge in edges if point in edge.points]) for point in points))
else:
    '''Min Distance'''
    m.setObjective(quicksum(edge.distance * edge.var for edge in edges))



for point in points:
    m.addConstr(quicksum(edge.var for edge in edges if point in edge.points) == 2)

for subset in powerset_points:
    if subset != [] and subset != points:
        m.addConstr(quicksum(edge.var for edge in edges if edge.points[0] in subset and edge.points[1] in subset) <= len(subset) - 1)

m.optimize()

tour_edges = []
for edge in edges:
    if edge.var.X == 1.0:
        tour_edges.append(edge)

tour = []
tour.append(tour_edges[0].points[0])
tour.append(tour_edges[0].points[1])
for i in range(0, len(points) - 1):
    for te in tour_edges:
        if te.points[0] == tour[-1] and te.points[1] != tour[-2]:
            tour.append(te.points[1])
            break
        elif te.points[1] == tour[-1] and te.points[0] != tour[-2]:
            tour.append(te.points[0])
            break
print(tour)

angles = caluculate_angle(tour[-2], tour[0], tour[1])
for i in range(1, len(tour) - 1):
    angles += caluculate_angle(tour[i - 1], tour[i], tour[i + 1])
print(angles)