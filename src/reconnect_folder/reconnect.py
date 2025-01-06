from reconnect_folder import reconnect_functions as rf
from reconnect_folder import reconnect_constraints as rc
from reconnect_folder import reconnect_classes as rclass
import gurobipy as gb



'''----Contansts----'''
MAX_COLORED_POINTS = 12
RATIO = 0.5



def optimize_the_closest(tour, center):
    tour = [rclass.Point(point[0], point[1]) for point in tour]
    tour.pop()
    center = rclass.Point(center[0], center[1])

    sorted_by_distance = rf.sort_tour(tour, center)
    red_points, blue_points = rf.get_red_blue_points(tour, sorted_by_distance, MAX_COLORED_POINTS)
    colored_points = rf.get_colored_points(red_points, blue_points)
    powerset_of_colored_points = rf.get_powerset(colored_points)
    list_of_lists = rf.get_list_of_blue_pairs(tour, red_points, blue_points)

    for i in range(3):

        '''----Model----'''
        env = gb.Env(empty=True)
        env.setParam('LogToConsole', 0)
        env.start()
        m = gb.Model(env=env)

        '''----Edges----'''
        blue_edges = rf.get_blue_edges(tour, blue_points, colored_points, m)
        virtual_edges = rf.get_virtual_edges(list_of_lists, m)
        real_edges = rf.get_real_edges(colored_points, list_of_lists, m)
        edges = rf.get_edges(real_edges, virtual_edges)
        real_edges_with_blue = rf.get_real_edges_with_blue(real_edges, blue_edges)

        '''----Contraints----'''
        rc.virtual_edges_are_true(virtual_edges, m)
        rc.blue_edges_are_true(blue_edges, m)
        rc.colored_points_have_two_edges(colored_points, edges, m)
        rc.constraints_for_subsets(powerset_of_colored_points, colored_points, edges, m)

        if i == 0:

            '''----Optimize Angles----'''
            rc.optimize_for_optimal_angles(real_edges_with_blue, colored_points, m)
            m.optimize()
            opt_angles_tour = rf.get_new_tour(real_edges, red_points, tour, blue_points, m)
            opt_angles_angles, opt_angles_distance = rf.get_angels_distance(opt_angles_tour)

        elif i == 1:

            '''----Optimize Distance----'''
            rc.optimize_for_optimal_distance(real_edges, m)
            m.optimize()
            opt_distance_tour = rf.get_new_tour(real_edges, red_points, tour, blue_points, m)
            opt_distance_angles, opt_distance_distance = rf.get_angels_distance(opt_distance_tour)

        else:

            '''----Optimize Ratio----'''
            rc.optimize_for_optimal_ration_angles_distance(RATIO, real_edges_with_blue, colored_points, real_edges, opt_angles_angles, opt_distance_distance, m)
            m.optimize()
            opt_ratio_tour = rf.get_new_tour(real_edges, red_points, tour, blue_points, m)
            opt_ratio_angles, opt_ratio_distance = rf.get_angels_distance(opt_ratio_tour)

    if rf.is_opt_angle_best_tour(opt_angles_angles, opt_angles_distance, opt_distance_angles, opt_distance_distance, opt_ratio_angles, opt_ratio_distance):
        return [tuple(point) for point in opt_angles_tour]
        
    if rf.is_opt_distance_best_tour(opt_angles_angles, opt_angles_distance, opt_distance_angles, opt_distance_distance, opt_ratio_angles, opt_ratio_distance):
        return [tuple(point) for point in opt_distance_tour]
        
    return [tuple(point) for point in opt_ratio_tour]
