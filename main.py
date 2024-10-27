from PIL import Image, ImageDraw
import CONST
from CONST import Coord, Edge
import random
import solver


class Img:
    def __init__(self, height: int = CONST.SCREEN_HEIGHT, width: int = CONST.SCREEN_WIDTH, count: int = CONST.COUNT) -> None:
        self.HEIGHT = height
        self.WIDTH = width
        self.img = Image.new(
            "RGB", (height, width), color="white")
        self._draw = ImageDraw.Draw(self.img)

        self.points = self.gernerte_point(count)
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
        self.img.save(name)

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
    img = Img()
    img.save("Test.jpg")
