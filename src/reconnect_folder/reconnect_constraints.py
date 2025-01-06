from reconnect_folder import reconnect_functions as rf
import gurobipy as gb



'''----Contraints----'''

def virtual_edges_are_true(virtual_edges, m):
    for edge in virtual_edges:
        m.addConstr(edge.var == 1)


def blue_edges_are_true(blue_edges, m):
    for edge in blue_edges:
        m.addConstr(edge.var == 1)


def colored_points_have_two_edges(colored_points, edges, m):
    for point in colored_points:
        m.addConstr(gb.quicksum(edge.var for edge in edges if point in edge.points) == 2)


def constraints_for_subsets(powerset_of_colored_points, colored_points, edges, m):
    for subset in powerset_of_colored_points:
        if len(subset) >= 1 and len(subset) <= len(colored_points) / 2:
            m.addConstr(gb.quicksum(edge.var for edge in edges if edge.points[0] in subset and edge.points[1] in subset) <= len(subset) - 1)


'''----Optimization----'''

def optimize_for_optimal_angles(real_edges_with_blue, colored_points, m):
    m.setObjective(gb.quicksum(rf.get_angle([edge for edge in real_edges_with_blue if point in edge.points]) for point in colored_points), gb.GRB.MINIMIZE)


def optimize_for_optimal_distance(real_edges, m):
    m.setObjective(gb.quicksum(edge.distance * edge.var for edge in real_edges), gb.GRB.MINIMIZE)


def optimize_for_optimal_ration_angles_distance(ratio, real_edges_with_blue, colored_points, real_edges, opt_angles_angles, opt_distance_distance, m):
    m.setObjective(ratio * opt_distance_distance * gb.quicksum(rf.get_angle([edge for edge in real_edges_with_blue if point in edge.points]) for point in colored_points) + (1 - ratio) * opt_angles_angles * gb.quicksum(edge.distance * edge.var for edge in real_edges), gb.GRB.MINIMIZE)
