import CONST
from image import Img
import argparse
import file
from CONST import Stats
import solver
import cpp_wrapper
import generate
from openpyxl import load_workbook


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-height",
        "-he",
        type = int,
        metavar = "INT",
        default = CONST.SCREEN_HEIGHT,
        help = f"int als Höhe (Default {CONST.SCREEN_HEIGHT})",
    )
    parser.add_argument(
        "-width",
        "-w",
        type = int,
        metavar = "INT",
        default = CONST.SCREEN_WIDTH,
        help = f"int als Breite (Default {CONST.SCREEN_WIDTH})",
    )
    parser.add_argument(
        "-count",
        "-c",
        type = int,
        metavar = "INT",
        default = CONST.POLYGON_COUNT,
        help = f"anzahl der kreuze (Default {CONST.POLYGON_COUNT})",
    )
    parser.add_argument(
        "-name",
        type = str,
        metavar = "STR",
        default = CONST.DATEI_NAME,
        help = f"Name der output Datei (Default {CONST.DATEI_NAME})",
    )
    parser.add_argument(
        "-opt",
        "-o",
        type = int,
        metavar = "INT",
        default = 4,
        help = f"Wie viele Schritte ausgeführt werden sollen: 0: polygone, 1: farthest, 2: r&r, 3: 2opt, >4: alle (Default Alle)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-file",
        "-f",
        type = str,
        metavar = "STR",
        help = "Name der input Datei",
    )
    group.add_argument(
        "-neu", "-n",
        action = "store_true",
        help = "ob neue Punkte generiert werden sollen"
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



def run_algo(polygon_list, best_polygon_list, args, print_st: bool = True, save: bool = True, name="") -> list[Stats]:
    result = []
    all_points = [i.hull for i in best_polygon_list]
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
        result.append(Stats(dis, angle))
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

    if args.opt >=4:
        points = solver.gurobi_solver(all_points, points)
        if save:
            img = Img(polygon_list, points, args.height, args.width)
            img.save(args.name+"04_gurobi")
        dis, angle = solver.calculate_dis_angle(points)
        result.append(Stats(dis, angle))
        if print_st:
            CONST.prints_stats(name + " gurobi", dis, angle)

    if not save:
        img = Img(polygon_list, points, args.height, args.width)
        img.save(name)

    return result


if __name__ == "__main__":
    args = parse_args()

    if args.file != None:
        polygon_list = file.read_polygons(args.file)
        best_polygon_list = generate.find_best_polygon_list(polygon_list)
        
        img = Img(polygon_list, [], args.height, args.width)
        img.save(args.name + "00_all_polygons")
        img = Img(best_polygon_list, [], args.height, args.width)
        img.save(args.name + "00_best_polygons")

        if args.opt != 0:
            run_algo(polygon_list, best_polygon_list, args)
    elif args.neu:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        polygon_list = generate.generate_polygons(args.count, height, width)
        best_polygon_list = generate.find_best_polygon_list(polygon_list)
        file.write_polygons(polygon_list, f"new_{args.name}")

        img = Img(polygon_list, [], args.height, args.width)
        img.save(args.name + "00_all_polygons")
        img = Img(best_polygon_list, [], args.height, args.width)
        img.save(args.name + "00_best_polygons")
        print("New polygons have been generated")

        if args.opt != 0:
            run_algo(polygon_list, best_polygon_list, args)
    else:
        # Load the existing workbook
        workbook = load_workbook("result.xlsx")
        # Select the active worksheet (or specify by name: workbook["SheetName"])
        sheet = workbook.active
        ROW = 8
        COLUME_DIS = "K"
        COLUME_ANGLE = "L"

        for i in range(20):
            polygon_list = file.read_polygons(f"standard_test_{i}")
            best_polygon_list = generate.find_best_polygon_list(polygon_list)
            result = run_algo(polygon_list, best_polygon_list, args,
                              save=False, name=f"standard_test_{i}")
            sheet[f"{COLUME_DIS}{ROW + i}"] = result[-1].dist
            sheet[f"{COLUME_ANGLE}{ROW + i}"] = result[-1].angle
            # Save the changes
            workbook.save("result.xlsx")
            print("----------------------------------------")


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
