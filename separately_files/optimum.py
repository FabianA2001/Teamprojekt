import gurobipy as gb
import random
import optimum_assistance as oa
import time


start_time = time.time()


env = gb.Env(empty=True)
env.setParam('LogToConsole', 0)
env.start()

m = gb.Model(env=env)

points = []
for i in range(12):
    points.append(oa.Point(random.randint(0, 10000), random.randint(0, 10000)))

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
        edges.append(oa.Edge([points[i], points[j]], m))

for point in points:
    m.addConstr(gb.quicksum(edge.var for edge in edges if point in edge.points) == 2)

for subset in powerset_points:
    if len(subset) >= 3 and subset != points:
        m.addConstr(gb.quicksum(edge.var for edge in edges if edge.points[0] in subset and edge.points[1] in subset) <= len(subset) - 1)


m.setObjective(gb.quicksum(edge.distance * edge.var for edge in edges))
m.optimize()
optDist_angle, optDist_distance, optDist_tour = oa.get_angels_distance(edges, points)


m.setObjective(gb.quicksum(oa.get_angle([edge for edge in edges if point in edge.points]) for point in points))
m.optimize()
optAngle_angle, optAngle_distance, optAngle_tour = oa.get_angels_distance(edges, points)


ratio = 0.5
m.setObjective(ratio * optDist_distance * gb.quicksum(oa.get_angle([edge for edge in edges if point in edge.points]) for point in points) + (1.0 - ratio) * optAngle_angle * gb.quicksum(edge.distance * edge.var for edge in edges))
m.optimize()
optRatio_angle, optRatio_distance, optRatio_tour = oa.get_angels_distance(edges, points)


print("Optimal Distance:")
print(f" Distance: {optDist_distance}")
print(f" Angles  : {optDist_angle}")
print(optDist_tour)
print()
print("Optimal Angles:")
print(f" Distance: {optAngle_distance}")
print(f" Angles  : {optAngle_angle}")
print(optAngle_tour)
print()
print("Optimal Ratio:")
print(f" Distance: {optRatio_distance}")
print(f" Angles  : {optRatio_angle}")
print(optRatio_tour)
print()
print("Time:")
duration_time = time.time() - start_time
print(f" {duration_time}")
