from PIL import Image, ImageDraw
import CONST
from CONST import Coord, Edge
import random
import solver
import argparse
import file
import math


class Img:
    def __init__(self, height: int = CONST.SCREEN_HEIGHT, width: int = CONST.SCREEN_WIDTH, count: int = CONST.COUNT, points: list[Coord] = []) -> None:
        self.HEIGHT = height * CONST.ANTIALIAS_FACTOR
        self.WIDTH = width * CONST.ANTIALIAS_FACTOR
        self.HEIGHT_ORGINAL = height
        self.WIDTH_ORGINAL = width
        self.img = Image.new(
            "RGB", (self.HEIGHT, self.WIDTH), color="white")
        self._draw = ImageDraw.Draw(self.img)

        if points == []:
            self.points = self.generate_point(count)
        else:
            self.points = points

        self.edges = solver.solver(self.points)

        self._draw_image()

    def calculate_distance(self, point1: Coord, point2: Coord) -> float:
        distance = math.sqrt(
            math.pow((point1.x - point2.x), 2) + math.pow((point1.y - point2.y), 2))
        return distance

    def generate_point(self, count: int) -> list[Coord]:
        OFFSET = 20 * CONST.ANTIALIAS_FACTOR
        list = []

        def enough_distance() -> bool:
            for point in list:
                if self.calculate_distance(coord, point) <= CONST.MIN_DISTANCE:
                    return False
            return True

        for _ in range(count):
            for _ in range(100):
                coord = Coord(random.randint(OFFSET, self.HEIGHT-OFFSET),
                              random.randint(OFFSET, self.WIDTH-OFFSET))
                if enough_distance() == True:
                    break
            list.append(coord)
        return list

    def show(self):
        self.img.show()

    def save(self, name: str):

        self.img = self.img.resize(
            (self.HEIGHT_ORGINAL, self.WIDTH_ORGINAL), Image.LANCZOS)
        self.img.save(name+".jpg")
        file.write(self.points, name)

    def _draw_image(self):
        for edge in self.edges:
            self._connect_points(edge)

        for coord in self.points:
            self._draw_ellipse(coord)

    def _draw_point_debugg(self, x, y):
        self._draw.line((0, y, self.img.width, y), fill="red")
        self._draw.line((x, 0, x, self.img.height), fill="red")

    def _draw_cross(self, coord: Coord) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = 20//2
        self._draw.line((coord.x-SIZE, coord.y-SIZE, coord.x + SIZE, coord.y+SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)
        self._draw.line((coord.x-SIZE, coord.y+SIZE, coord.x + SIZE, coord.y-SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)

    def _draw_ellipse(self, coord: Coord) -> None:
        LINE_COLOR = "red"
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = (20 * CONST.ANTIALIAS_FACTOR)//2
        self._draw.ellipse((coord.x-SIZE, coord.y-SIZE, coord.x + SIZE, coord.y+SIZE),
                           fill=LINE_COLOR, width=LINE_WIDTH)

    def _connect_points(self, edge: Edge) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 7 * CONST.ANTIALIAS_FACTOR
        self._draw.line((edge.point1.x, edge.point1.y, edge.point2.x,
                        edge.point2.y), fill=LINE_COLOR, width=LINE_WIDTH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-height", "-he", type=int, metavar="INT",
                        default=CONST.SCREEN_HEIGHT, help=f"int als Höhe (Default {CONST.SCREEN_HEIGHT})")
    parser.add_argument("-width", "-w", type=int, metavar="INT",
                        default=CONST.SCREEN_WIDTH, help=f"int als Breite (Default {CONST.SCREEN_WIDTH})")
    parser.add_argument("-count", "-c", type=int, metavar="INT",
                        default=CONST.COUNT, help=f"anzahl der kreuze (Default {CONST.COUNT})")
    parser.add_argument("-name", "-n", type=str, metavar="STR",
                        default=CONST.DATEI_NAME, help=f"Name der output Datei (Default {CONST.DATEI_NAME})")
    parser.add_argument("-file", "-f", type=str, metavar="STR",
                        help=f"Name der input Datei")

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

    points = []
    if args.file != None:
        points = file.read(args.file)

    img = Img(args.height, args.width, args.count, points)
    img.save(args.name)
