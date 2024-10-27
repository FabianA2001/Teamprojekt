from PIL import Image, ImageDraw
import CONST
from CONST import Coord, Edge
import random
import solver
import argparse
import file


class Img:
    def __init__(self, height: int = CONST.SCREEN_HEIGHT, width: int = CONST.SCREEN_WIDTH, count: int = CONST.COUNT, points: list[Coord] = []) -> None:
        self.HEIGHT = height
        self.WIDTH = width
        self.img = Image.new(
            "RGB", (height, width), color="white")
        self._draw = ImageDraw.Draw(self.img)

        if points == []:
            self.points = self.gernerte_point(count)
        else:
            self.points = points

        for coord in self.points:
            self._draw_cross(coord)

        self.edges = solver.solver(self.points)
        for edge in self.edges:
            self._connect_points(edge)

    def gernerte_point(self, count: int) -> list[Coord]:
        DISTANCE = 10
        list = []
        for _ in range(count):
            while True:
                coord = Coord(random.randint(0, self.HEIGHT),
                              random.randint(0, self.WIDTH))
                if "genügend dis":
                    break
            list.append(coord)
        return list

    def show(self):
        self.img.show()

    def save(self, name: str):
        self.img.save(name+".jpg")
        file.write(self.points, name)

    def _draw_point_debugg(self, x, y):
        self._draw.line((0, y, self.img.width, y), fill="red")
        self._draw.line((x, 0, x, self.img.height), fill="red")

    def _draw_cross(self, coord: Coord) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 2
        SIZE = 10//2
        self._draw.line((coord.x-SIZE, coord.y-SIZE, coord.x + SIZE, coord.y+SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)
        self._draw.line((coord.x-SIZE, coord.y+SIZE, coord.x + SIZE, coord.y-SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)

    def _connect_points(self, edge: Edge) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 2
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
