from PIL import Image, ImageDraw
import CONST
import random


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Edge:
    def __init__(self, point1: Coord, point2: Coord, length: float) -> None:
        self.point1 = point1
        self.point2 = point2
        self.length = length


class Img:
    def __init__(self, height: int = CONST.SCREEN_HEIGHT, width: int = CONST.SCREEN_WIDTH, count: int = CONST.COUNT) -> None:
        self.HEIGHT = height
        self.WIDTH = width
        self.img = Image.new(
            "RGB", (height, width), color="white")
        self._draw = ImageDraw.Draw(self.img)

        for coord in self.gernerte_point(count):
            self._draw_cross(coord.x, coord.y)

        # self._connect_points(100, 200, 200, 600)

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

    def _draw_point_debugg(self, x, y):
        self._draw.line((0, y, self.img.width, y), fill="red")
        self._draw.line((x, 0, x, self.img.height), fill="red")

    def _draw_cross(self, x: int, y: int) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 2
        SIZE = 10//2
        self._draw.line((x-SIZE, y-SIZE, x + SIZE, y+SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)
        self._draw.line((x-SIZE, y+SIZE, x + SIZE, y-SIZE),
                        fill=LINE_COLOR, width=LINE_WIDTH)

    # def _draw_cross(self, coord: Coord) -> None:
    #     self._draw_cross(coord.x, coord.y)

    def _connect_points(self, x1: int, y1: int, x2: int, y2: int) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 2
        self._draw.line((x1, y1, x2, y2), fill=LINE_COLOR, width=LINE_WIDTH)


if __name__ == "__main__":
    img = Img()
    img.img.save("Test.jpg")
