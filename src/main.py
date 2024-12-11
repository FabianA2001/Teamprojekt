import CONST
from image import Img
import argparse
import file
from CONST import Coord
import math
import solver
import cpp_wrapper
import gurobipy as gp
from gurobipy import GRB
from generate import generate_areas


def to_coord(tuples) -> list[Coord]:
    coords = []
    for tuple in tuples:
        coords.append(Coord(tuple[0], tuple[1]))
    return coords


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-height",
        "-he",
        type=int,
        metavar="INT",
        default=CONST.SCREEN_HEIGHT,
        help=f"int als Höhe (Default {CONST.SCREEN_HEIGHT})",
    )
    parser.add_argument(
        "-width",
        "-w",
        type=int,
        metavar="INT",
        default=CONST.SCREEN_WIDTH,
        help=f"int als Breite (Default {CONST.SCREEN_WIDTH})",
    )
    parser.add_argument(
        "-count",
        "-c",
        type=int,
        metavar="INT",
        default=CONST.AREA_COUNT,
        help=f"anzahl der kreuze (Default {CONST.AREA_COUNT})",
    )
    parser.add_argument(
        "-name",
        type=str,
        metavar="STR",
        default=CONST.DATEI_NAME,
        help=f"Name der output Datei (Default {CONST.DATEI_NAME})",
    )
    parser.add_argument(
        "-opt",
        "-o",
        action="store_false",
        help="Ob keine Ruin und Create verbesserung vorgenommen werden soll",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-file",
        "-f",
        type=str,
        metavar="STR",
        help="Name der input Datei",
    )
    group.add_argument(
        "-neu", "-n",
        action="store_true",
        help="ob neue Punkte generiert werden sollen"
    )

    args = parser.parse_args()
    if args.height < 50:
        raise argparse.ArgumentTypeError("Bitte eine größere Höhe")
    if args.width < 50:
        raise argparse.ArgumentTypeError("Bitte eine größere Breite")
    if args.count <= 2:
        raise argparse.ArgumentTypeError("Bitte mehr als 2 Punkte")
    if args.name == "":
        raise argparse.ArgumentTypeError("Bitte keinene leeren Namen")
    if args.file != None and args.file == "":
        raise argparse.ArgumentTypeError("Bitte keinene leeren file Namen")

    return args


def prints_stats(name: str, dis, angle):
    print(f"Distance: {round(dis, 2)}\tAngle: {round(angle, 2)}\t{name}")


def gurobi_solver(pointslist: list[list[Coord]], orderlist: list[Coord]):
    model = gp.Model()
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
                dist += solver.calculate_distance(
                    point1, point2) * vars[point1] * vars[point2]

    # for i in range(len(order)-2):
    #    for point1 in order[i]:
    #        for point2 in order[(i+1) % len(order)]:
    #            for point3 in order[(i+2) % len(order)]:
    #            dist = solver.calculate_distance(
    #                point1, point2) * vars[point1] * vars[point2]

    # print(order)
    # Solution
    model.setObjective(dist, GRB.MINIMIZE)
    model.optimize()
    retpoints = []

    for pointss in order:
        for point in pointss:
            # print("h", vars[point], vars[point].X)
            if vars[point].X > 0.5:
                retpoints.append(point)

    return retpoints


class Stats:
    def __init__(self, dist, angle) -> None:
        self.dist = dist
        self.angle = angle


def run_algo(all_points: list[list[Coord]], print_st: bool = True, save: bool = True) -> list[Stats]:
    result = []

    points = cpp_wrapper.get_midpoints_from_areas(
        [[tuple(i) for i in area] for area in all_points])
    points = to_coord(points)

    points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
    points = to_coord(points)
    if save:
        img = Img(all_points, points, args.height, args.width)
        img.save(args.name+"01farthest_insertion")
    dis, angle = solver.calculate_dis_angle(points)
    result.append(Stats(dis, angle))
    if print_st:
        prints_stats("farthest insertion", dis, angle)

    points = cpp_wrapper.ruin_and_recreate(
        [tuple(i) for i in points], 3000, 0.3, 1.2)
    points = to_coord(points)
    if save:
        img = Img(all_points, points, args.height, args.width)
        img.save(args.name+"02ruin&recreate")
    dis, angle = solver.calculate_dis_angle(points)
    result.append(Stats(dis, angle))
    if print_st:
        prints_stats("ruin & recreate", dis, angle)

    points = cpp_wrapper.two_opt([tuple(i) for i in points])
    points = to_coord(points)
    if save:
        img = Img(all_points, points, args.height, args.width)
        img.save(args.name+"03two_opt")
    dis, angle = solver.calculate_dis_angle(points)
    result.append(Stats(dis, angle))
    if print_st:
        prints_stats("two opt", dis, angle)

    points = gurobi_solver(all_points, points)
    if save:
        img = Img(all_points, points, args.height, args.width)
        img.save(args.name+"04gurobi")
    dis, angle = solver.calculate_dis_angle(points)
    result.append(Stats(dis, angle))
    if print_st:
        prints_stats("gurobi", dis, angle)
    return result


if __name__ == "__main__":
    args = parse_args()

    if args.file != None:
        all_points = file.read(args.file)
        run_algo(all_points)
    elif args.neu:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        all_points = generate_areas(args.count, height, width)

        file.write_all_points(all_points, args.name)
        img = Img(all_points, [], args.height, args.width)
        img.save(args.name + "00points")
        print("New points have been generated")
        run_algo(all_points)
    else:
        pass
