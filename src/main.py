import CONST
from image import Img
import argparse
import file
from CONST import Coord, Polygon
import solver
import cpp_wrapper
import gurobipy as gp
from gurobipy import GRB
from generate import generate_polygons


def to_coord(tuples):
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
        default=CONST.POLYGON_COUNT,
        help=f"anzahl der kreuze (Default {CONST.POLYGON_COUNT})",
    )
    parser.add_argument(
        "-name",
        "-n",
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
    parser.add_argument(
        "-file",
        "-f",
        type=str,
        metavar="STR",
        help="Name der input Datei",
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


if __name__ == "__main__":
    args = parse_args()

    if args.file != None:
        polygon_list = file.read_polygons(args.file)   
    else:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        polygon_list = generate_polygons(args.count, height, width)
        file.write_polygons(polygon_list, args.name)
        print("New polygons have been generated")
         
    

    #img = Img(polygon_list,[], args.height, args.width)
    #img.save(args.name + "00polygons")


    """
    points = cpp_wrapper.get_midpoints_from_areas(
        [[tuple(i) for i in area] for area in all_points])
    points = to_coord(points)


    file.write(points, args.name)
    points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"01farthest_insertion")
    prints_stats("farthest insertion", points)
    
    points = cpp_wrapper.ruin_and_recreate(
        [tuple(i) for i in points], 3000, 0.3, 1.2)
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"02ruin&recreate")
    prints_stats("ruin & recreate", points)

    points = cpp_wrapper.two_opt([tuple(i) for i in points])
    points = to_coord(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"03two_opt")
    prints_stats("two opt", points)

    
    points = gurobi_solver(all_points, points)
    # print(points)
    img = Img(all_points, points, args.height, args.width)
    img.save(args.name+"04gurobi")
    prints_stats("gurobi", points)
    #"""