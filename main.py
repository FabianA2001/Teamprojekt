from PIL import Image, ImageDraw, ImageFont
import CONST


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
    def __init__(self, height: int = CONST.SCREEN_HEIHT, width: int = CONST.SCREEN_WITH, count: int = CONST.COUNT) -> None:
        self.HEIGHT = height
        self.WIDTH = width
        self.img = Image.new(
            "RGB", (height, width), color="white")
        self._draw = ImageDraw.Draw(self.img)

        for x, y in self.gernerte_point(CONST.SCREEN_HEIHT, CONST.SCREEN_WITH, count):
            self._draw_cross(x, y)

        self._connect_points(100, 200, 200, 600)

    def gernerte_point(self, height, withe, count) -> list[tuple[int, int]]:
        return [(100, 200), (200, 600)]

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

    def _connect_points(self, x1: int, y1: int, x2: int, y2: int) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 2
        self._draw.line((x1, y1, x2, y2), fill=LINE_COLOR, width=LINE_WIDTH)


if __name__ == "__main__":
    img = Img()
    img.img.save("Test.jpg")
