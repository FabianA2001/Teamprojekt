import CONST
from image import Img
import argparse
import file
import random
from CONST import Coord, Edge
import math
import solver


def calculate_distance(point1: Coord, point2: Coord) -> float:
    distance = math.sqrt(
        math.pow((point1.x - point2.x), 2) +
        math.pow((point1.y - point2.y), 2)
    )
    return distance


def is_enough_distance(coord1: Coord, coord2: Coord, distance: int) -> bool:
    if calculate_distance(coord1, coord2) >= distance:
        return True
    return False


def generate_areas(count: int, height: int, width: int) -> list[Coord]:
    OFFSET = (CONST.OFFSET + CONST.CLUSTER_RADUIS) * CONST.ANTIALIAS_FACTOR
    areas_list = []
    verifier = True

    for _ in range(count):
        for attempt in range(100):
            area_location = Coord(
                random.randint(OFFSET, height - OFFSET),
                random.randint(OFFSET, width - OFFSET),
            )
            for location in areas_list:
                if attempt == 0:
                    continue
                if is_enough_distance(area_location, location, CONST.MIN_DISTANCE_AREA):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster = generate_cluster(CONST.CLUSTER_SIZE, area_location)
                areas_list.append(cluster)
                break
    return areas_list
          

def generate_cluster(count: int, center: Coord) -> list[Coord]:
    cluster_list = []
    verifier = True

    for _ in range(count):
        for attempt in range(100):
            cluster_point = Coord(
                random.randint(center.x - CONST.CLUSTER_RADUIS, center.x + CONST.CLUSTER_RADUIS),
                random.randint(center.y - CONST.CLUSTER_RADUIS, center.y + CONST.CLUSTER_RADUIS),
            )
            for point in cluster_list:
                if attempt == 0:
                    continue
                if is_enough_distance(cluster_point, point, CONST.MIN_DISTANCE_CLUSTER):
                    verifier = True
                else:
                    verifier = False
                    break
            if verifier == True:
                cluster_list.append(cluster_point)
                break
    return cluster_list


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
    if args.file != None:
        points = file.read(args.file)
    else:
        height = args.height * CONST.ANTIALIAS_FACTOR
        width = args.width * CONST.ANTIALIAS_FACTOR
        points = generate_areas(args.count, height, width)

    img = Img(points, args.height, args.width)
    img.save(args.name+"points")
    

    """
    points = solver.farthest_insertion(points)
    img = Img(points, args.height, args.width)
    img.save(args.name+"farthest")
    prints_stats("farthest", points)

    points = solver.ruin_and_recreate(points)[0]
    img = Img(points, args.height, args.width)
    img.save(args.name+"ruin")
    prints_stats("ruin", points)

    points = solver.two_opt(points)
    img = Img(points, args.height, args.width)
    img.save(args.name+"two opt")
    prints_stats("two opt", points)
    """