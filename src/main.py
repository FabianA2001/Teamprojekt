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
import shapely.geometry as shap

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


def punkte_verschieben(polygon_list, points):
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
        current_angle = solver.caluculate_angle(
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
                new_angle = solver.caluculate_angle(
                    points[i-1], point, points[i+1])
                if new_angle < current_angle:
                    current_angle = new_angle
                    points[i] = point
    # for point in points:
    #     for p, polygon in enumerate(polygon_list):
    #         if generate.is_point_inside_polygon(polygon, point):
    #             print(p)

    return points



def tour_around_obstacles(obstacles, points):
    return generate.find_obstacle_plus_bypass(points, obstacles)



def run_algo(polygon_list, best_polygon_list, args, print_st: bool = True, save: bool = True, name="") -> list[Stats]:
    result = []
    all_points = [i.hull for i in best_polygon_list]
    points = [i.centroid for i in best_polygon_list]

    for index, point in enumerate(points):
        all_points[index].append(point)

    if args.opt >= 1:
        points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
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
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img.save(args.name+"02_ruin&recreate")
        dis, angle = solver.calculate_dis_angle(points)
        # result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " ruin & recreate", dis, angle)

    if args.opt >= 3:
        points = cpp_wrapper.two_opt([tuple(i) for i in points], 1.5)
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img.save(args.name+"03_two_opt")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " two opt", dis, angle)

    if args.opt >= 4:
        points = solver.gurobi_solver(all_points, points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img.save(args.name+"04_gurobi")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " gurobi", dis, angle)

    if args.opt >= 5:
        for i in range(6):
            center_point = cpp_wrapper.get_point_with_max_angle(
                [tuple(i) for i in points])
            points = reconnect.optimize_the_closest(
                [tuple(i) for i in points], tuple(center_point))

        center_point = Coord(center_point[0], center_point[1])
        points = CONST.to_coord(points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img._draw_point_debugg(center_point.x, center_point.y, "red")
            img.save(args.name+"05_reconnect_area")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " reconnect", dis, angle)
    if args.opt >= 6:
        points = punkte_verschieben(best_polygon_list, points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img.save(args.name+"06_punkte_verschieben")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " Punkte Verschieben", dis, angle)

    if args.opt >= 7:
        points = tour_around_obstacles(obstacle_list, points)
        if save:
            img = Img(polygon_list, obstacle_list, points, args.height, args.width)
            img.save(args.name+"07_around_obstacles")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " around obstacles", dis, angle)

    if not save:
        img = Img(polygon_list, obstacle_list, points, args.height, args.width)
        img.save(name)

    return result


if __name__ == "__main__":

    args = parse_args()

    if args.file != None:
        polygon_list = file.read_polygons(args.file)
        obstacle_list = file.read_polygons(f"{args.file}_obstacles")
        best_polygon_list = generate.find_best_polygon_list_2(polygon_list)
        print(f"Polygons have been read from {args.file} and {
              len(best_polygon_list)} intersections are essential")

        file.write_polygons(best_polygon_list, f"best_polygons_{args.name}")

        # need = file.read_polygons("test_einlesen")
        # bool_need = generate.is_polygon_inside_polygon(need[1], need[0])
        # print(generate.is_same_polygon(need[1], need[2]))

        if args.opt >= 0:
            img = Img(polygon_list, obstacle_list, [], args.height, args.width)
            img.save(args.name + "00_all_polygons")
            img = Img(best_polygon_list, obstacle_list,
                      best_polygon_list[1].hull, args.height, args.width)
            img.save(args.name + "00_best_polygons")

        if args.opt > 0:
            run_algo(polygon_list, best_polygon_list, args)
    elif args.neu:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        polygon_list = generate.generate_polygons(args.count, height, width)
        obstacle_list = generate.generate_polygons(CONST.OBSTACLE_COUNT, height, width)
        best_polygon_list = generate.find_best_polygon_list_2(polygon_list)
        file.write_polygons(polygon_list, f"new_{args.name}")
        file.write_polygons(best_polygon_list, f"new_{args.name}_best_poly")
        print(f"New polygons have been generated and {
              len(best_polygon_list)} intersections are essential")

        if args.opt >= 0:
            img = Img(polygon_list, obstacle_list, [], args.height, args.width)
            img.save(args.name + "00_all_polygons")
            img = Img(best_polygon_list, obstacle_list, [], args.height, args.width)
            img.save(args.name + "00_best_polygons")

        if args.opt > 0:
            run_algo(polygon_list, best_polygon_list, args)
    else:
        # Load the existing workbook
        workbook = load_workbook("result.xlsx")
        # Select the active worksheet (or specify by name: workbook["SheetName"])
        sheet = workbook.active
        ROW = 8
        COLUME_DIS = ["C", "E", "G", "I", "K"]
        COLUME_ANGLE = ["D", "F", "H", "J", "L"]

        for i in range(20):
            polygon_list = file.read_polygons(f"standard_test_{i}")
            best_polygon_list = generate.find_best_polygon_list_2(polygon_list)
            result = run_algo(polygon_list, best_polygon_list, args,
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
