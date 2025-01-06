import CONST
from image import Img
import argparse
import file
from CONST import Stats, Coord
import solver
import cpp_wrapper
import generate
from openpyxl import load_workbook
import math
from reconnect_folder import reconnect

import time
# Record the start time
start_time = time.time()


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
        type=str,
        metavar="STR",
        default=CONST.DATEI_NAME,
        help=f"Name der output Datei (Default {CONST.DATEI_NAME})",
    )
    parser.add_argument(
        "-opt",
        "-o",
        type=int,
        metavar="INT",
        default=math.inf,
        help=f"Wie viele Schritte ausgeführt werden sollen: 0: polygone, 1: farthest, 2: r&r, 3: 2opt, >4: alle (Default Alle)",
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


def newPoints(polygon_list, points):
    new_points = []

    for polygon in polygon_list:
        for point in points:
            if generate.is_point_inside_polygon(polygon, point):
                new_poly = []
                new_poly.append(point)
                i = 0
                while i < 5:
                    new_point = generate.random_coord_local(point, 500)
                    if generate.is_point_inside_polygon(polygon, new_point) and new_point not in new_poly:
                        new_poly.append(new_point)
                        i += 1
        new_points.append(new_poly)
    return new_points


def run_algo(polygon_list, args, print_st: bool = True, save: bool = True, name="") -> list[Stats]:
    result = []
    all_points = [i.hull for i in polygon_list]
    points = cpp_wrapper.get_midpoints_from_areas(
        [[tuple(i) for i in area] for area in all_points])
    points = CONST.to_coord(points)

    if args.opt >= 1:
        points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.save(args.name+"01_farthest_insertion")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " farthest insertion", dis, angle)

    if args.opt >= 2:
        points = cpp_wrapper.ruin_and_recreate(
            [tuple(i) for i in points], 3000, 0.3, 1.2)
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.save(args.name+"02_ruin&recreate")
        dis, angle = solver.calculate_dis_angle(points)
        # result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " ruin & recreate", dis, angle)

    if args.opt >= 3:
        points = cpp_wrapper.two_opt([tuple(i) for i in points], 1.5)
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.save(args.name+"03_two_opt")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " two opt", dis, angle)

    if args.opt >= 4:
        points = solver.gurobi_solver(all_points, points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.save(args.name+"04_gurobi")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " gurobi", dis, angle)

    if args.opt >= 5:
        # order: list[list[Coord]] = []
        # dist = 0
        # for opoint in points:
        #     for ppoints in all_points:
        #         for point in ppoints:
        #             if opoint.x == point.x and opoint.y == point.y:
        #                 order.append(ppoints)
        # all_points = order

        # all_points_con = []
        # for area in all_points:
        #     temp = []
        #     for coord in area:
        #         temp.append(tuple(coord))
        #     all_points_con.append(temp)

        # points, center_point, corner_points = cpp_wrapper.radius_tour(
        #     all_points_con, [tuple(i) for i in points], 4000.0)

        for i in range(6):
            center_point = cpp_wrapper.get_point_with_max_angle(
                [tuple(i) for i in points])
            points = reconnect.optimize_the_closest(
                [tuple(i) for i in points], tuple(center_point))

        center_point = Coord(center_point[0], center_point[1])
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.draw_point_debugg(center_point.x, center_point.y, "red")
            img.save(args.name+"05_reconnect_area")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " reconnect", dis, angle)

    if not save:
        img = Img(polygon_list, points, args.height, args.width)
        img.save(args.name+name)

    return result


if __name__ == "__main__":

    args = parse_args()

    if args.file != None:
        polygon_list = file.read_polygons(args.file)
        img = Img(polygon_list, [], args.height, args.width)
        img.save(args.name + "00_polygons")
        if args.opt != 0:
            run_algo(polygon_list, args)
    elif args.neu:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        polygon_list = generate.generate_polygons(args.count, height, width)

        file.write_polygons(polygon_list, f"new_{args.name}")
        img = Img(polygon_list, [], args.height, args.width)
        img.save(args.name + "00_polygons")
        print("New polygons have been generated")
        if args.opt != 0:
            run_algo(polygon_list, args)
    else:
        # Load the existing workbook
        workbook = load_workbook("result.xlsx")
        # Select the active worksheet (or specify by name: workbook["SheetName"])
        sheet = workbook.active
        ROW = 8
        COLUME_DIS = ["C", "E", "G", "I"]
        COLUME_ANGLE = ["D", "F", "H", "J"]

        for i in range(20):
            polygon_list = file.read_polygons(f"standard_test_{i}")
            result = run_algo(polygon_list, args,
                              save=False, name=f"standard_test_{i}")
            assert (len(COLUME_ANGLE) == len(result))
            for dis, angle, stat in zip(COLUME_DIS, COLUME_ANGLE, result):
                sheet[f"{dis}{ROW + i}"] = stat.dist
                sheet[f"{angle}{ROW + i}"] = stat.angle
        # Save the changes
            workbook.save("result.xlsx")
            # Calculate the elapsed time
            elapsed_time = int(time.time() - start_time)
            # Print the elapsed time
            print(f"Fertig nach {int(elapsed_time/60)}m {elapsed_time % 60}s")


"""
neu ruin&recreate(idenizifzieren wo ändern) Basti,Fabian (Caro)
nur überlappung wen möglich am anfang Torben
punkte in polygone verschieben Caro
längere objekte Torben
jedes Polygon hat mittelpunkt Torben




ruin & recreate

max angle finden -> Radius polygone auswähen
auf diesen Kreis bilden
mit gurobi wieder einfügen

"""
