import CONST
from image import Img
import argparse
import file
import random
from CONST import Coord, Edge
import math
import solver
import cpp_wrapper
import gurobipy as gp
from gurobipy import GRB
from generate import generate_areas


def calculate_distance(point1: Coord, point2: Coord) -> float:
    distance = math.sqrt(
        math.pow((point1.x - point2.x), 2) +
        math.pow((point1.y - point2.y), 2)
    )
    return distance


def to_coord(tuples):
    coords = []
    for tuple in tuples:
        coords.append(Coord(tuple[0], tuple[1]))
    return coords


def generate_point(count: int, height: int, width: int) -> list[Coord]:
    OFFSET = CONST.OFFSET * CONST.ANTIALIAS_FACTOR
    list = []

    def enough_distance() -> bool:
        for point in list:
            if (
                calculate_distance(coord, point)
                <= CONST.MIN_DISTANCE * CONST.ANTIALIAS_FACTOR
            ):
                return False
        return True

    for _ in range(count):
        for _ in range(100):
            coord = Coord(
                random.randint(OFFSET, height - OFFSET),
                random.randint(OFFSET, width - OFFSET),
            )
            if enough_distance() == True:
                break
        list.append(coord)
    return list


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
        "-n",
        type=str,
        metavar="STR",
        default=CONST.DATEI_NAME,
        help=f"Name der output Datei (Default {CONST.DATEI_NAME})",
    )
    parser.add_argument("-opt", "-o", action="store_false",
                        help="Ob keine Ruin und Create verbesserung vorgenommen werden soll")
    parser.add_argument(
        "-file", "-f", type=str, metavar="STR", help="Name der input Datei"
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


def prints_stats(name: str, points: list[Coord]):
    dis, angle = solver.calculate_dis_angle(points)
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
    order = []
    dist = 0
    for opoint in orderlist:
        for ppoints in pointslist:
            for point in ppoints:
                if opoint.x == point.x and opoint.y == point.y:
                    order.append(ppoints)
    for i in range(len(order)-1):
        for point in order[i]:
            # if vars[point] == 1:
            point1 = point
        for point in order[(i+1) % len(order)]:
            # if vars[point] == 1:
            point2 = point
        dist += (math.sqrt((point1.x - point2.x) ** 2 +
                           (point1.y - point2.y) ** 2)) * (vars[point1]+vars[point2])
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


if __name__ == "__main__":
    args = parse_args()

    if args.file != None:
        points = file.read(args.file)
        print("Dieses Programm funktioniert für Areas, die zufällig generiert werden, weswegen keine Punkte angegeben werden müssen.")
        quit()

    height = args.height * CONST.ANTIALIAS_FACTOR
    width = args.width * CONST.ANTIALIAS_FACTOR
    all_points = generate_areas(args.count, height, width)

    file.write_all_points(all_points, args.name)

    points = cpp_wrapper.get_midpoints_from_areas(
        [[tuple(i) for i in area] for area in all_points])
    points = to_coord(points)

    file.write(points, args.name)
    points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"farthest")
    prints_stats("farthest", points)

    points = cpp_wrapper.ruin_and_recreate(
        [tuple(i) for i in points], 3000, 0.3, 1.2)
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"ruin")
    prints_stats("ruin", points)

    points = cpp_wrapper.two_opt([tuple(i) for i in points])
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"two_opt")
    prints_stats("two opt", points)

    points = gurobi_solver(all_points, points)
    # print(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"gurobi")
    prints_stats("gurobi", points)
