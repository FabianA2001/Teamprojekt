from PIL import Image, ImageDraw, ImageFont
import solver
from CONST import Coord, Edge

import file
import CONST


class Img:
    def __init__(
        self,
        points: list[Coord],
        height: int = CONST.SCREEN_HEIGHT,
        width: int = CONST.SCREEN_WIDTH
    ) -> None:
        self.HEIGHT = height * CONST.ANTIALIAS_FACTOR
        self.WIDTH = width * CONST.ANTIALIAS_FACTOR
        self.HEIGHT_ORGINAL = height
        self.WIDTH_ORGINAL = width
        self.font = ImageFont.truetype(
            "LEMONMILK-Regular.otf", CONST.FONT_SIZE * CONST.ANTIALIAS_FACTOR
        )
        self.img = Image.new("RGB", (self.HEIGHT, self.WIDTH), color="white")
        self._draw = ImageDraw.Draw(self.img)
        self.points = points
        self.edges = solver.make_edges(points)

        self._draw_image()

    def show(self):
        self.img.show()

    def save(self, name: str):
        self.img = self.img.resize(
            (self.HEIGHT_ORGINAL, self.WIDTH_ORGINAL), Image.LANCZOS
        )
        self.img.save(name + ".jpg")
        file.write(self.points, name)

    def _draw_image(self):
        for edge in self.edges:
            self._connect_points(edge)

        for coord in self.points:
            self._draw_ellipse(coord)

        for i, coord in enumerate(self.edges):
            if i == len(self.edges) - 1:
                continue
            self._draw_number(coord.point1, i)

    def _draw_point_debugg(self, x, y):
        self._draw.line((0, y, self.img.width, y), fill="red")
        self._draw.line((x, 0, x, self.img.height), fill="red")

    def _draw_number(self, coord: Coord, nummer: int):
        self._draw.text((coord.x, coord.y), str(
            nummer), fill="red", font=self.font)

    def _draw_cross(self, coord: Coord) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = 20 // 2
        self._draw.line(
            (coord.x - SIZE, coord.y - SIZE, coord.x + SIZE, coord.y + SIZE),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )
        self._draw.line(
            (coord.x - SIZE, coord.y + SIZE, coord.x + SIZE, coord.y - SIZE),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )

    def _draw_ellipse(self, coord: Coord) -> None:
        LINE_COLOR = "red"
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = (10 * CONST.ANTIALIAS_FACTOR) // 2
        self._draw.ellipse(
            (coord.x - SIZE, coord.y - SIZE, coord.x + SIZE, coord.y + SIZE),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )

    def _connect_points(self, edge: Edge) -> None:
        LINE_COLOR = "black"
        LINE_WIDTH = 7 * CONST.ANTIALIAS_FACTOR
        self._draw.line(
            (edge.point1.x, edge.point1.y, edge.point2.x, edge.point2.y),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )
