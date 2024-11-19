import CONST
from image import Img
import argparse
import file
from CONST import Coord
import solver
from generate import generate_areas, get_point_from_cluster


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


if __name__ == "__main__":
    args = parse_args()
    height = args.height * CONST.ANTIALIAS_FACTOR
    width = args.width * CONST.ANTIALIAS_FACTOR

    if args.file != None:
        all_points = file.read(args.file)
    else:
        all_points = generate_areas(args.count, height, width)


    needed_points = get_point_from_cluster(all_points)


    #Erstellt ein Bild nur mit den Punkten
    img = Img(all_points,[], args.height, args.width)
    img.save(args.name+"points")
    

    #Erstellte ein Bild mit der Route nach farthest insertion
    needed_points = solver.farthest_insertion(needed_points)
    img = Img(all_points,needed_points, args.height, args.width)
    img.save(args.name+"farthest")
    prints_stats("farthest", needed_points)


    #Erstellt ein Bild mit der Route nach R&R
    needed_points = solver.ruin_and_recreate(needed_points)[0]
    img = Img(all_points,needed_points, args.height, args.width)
    img.save(args.name+"ruin")
    prints_stats("ruin", needed_points)


    #Erstellt ein Bild mit der Route nach Two Opt
    needed_points = solver.two_opt(needed_points)
    img = Img(all_points,needed_points, args.height, args.width)
    img.save(args.name+"two opt")
    prints_stats("two opt", needed_points)
    
