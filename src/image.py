from PIL import Image, ImageDraw, ImageFont
from CONST import Coord, Edge
import file
import CONST
import random


class Img:
    def __init__(
        self,
        all_points: list[list[Coord]],
        points_in_route: list[Coord],
        height: int = CONST.SCREEN_HEIGHT,
        width: int = CONST.SCREEN_WIDTH
    ) -> None:
        self.all_points = all_points
        self.points_in_route = points_in_route
        self.HEIGHT = height * CONST.ANTIALIAS_FACTOR
        self.WIDTH = width * CONST.ANTIALIAS_FACTOR
        self.HEIGHT_ORGINAL = height
        self.WIDTH_ORGINAL = width
        self.font = ImageFont.truetype(
            CONST.FONT_PRE+"LEMONMILK-Regular.otf", CONST.FONT_SIZE * CONST.ANTIALIAS_FACTOR
        )
        self.img = Image.new("RGB", (self.HEIGHT, self.WIDTH), color="white")
        self._draw = ImageDraw.Draw(self.img)
        self.edges = CONST.make_edges(self.points_in_route)

        self._draw_points()
        self._draw_route()

    def show(self) -> None:
        self.img.show()

    def save(self, name: str) -> None:
        self.img = self.img.resize(
            (self.HEIGHT_ORGINAL, self.WIDTH_ORGINAL), Image.LANCZOS
        )
        self.img.save(CONST.IMAGE_PRE+name + ".jpg")
        # TODO write anpassen
        # file.write(self.points_in_route, name)

    def _draw_points(self) -> None:
        def random_blue():
            red = random.randint(0, 50)
            green = random.randint(0, 100)
            blue = random.randint(100, 255)
            color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
            return color

        for i in range(CONST.AREA_COUNT):
            cluster_color = random_blue()
            for j in range(CONST.CLUSTER_SIZE):
                self._draw_ellipse(self.all_points[i][j], cluster_color)

    def _draw_route(self) -> None:
        for edge in self.edges:
            self._draw_edge(edge, "black")

        for coord in self.points_in_route:
            self._draw_ellipse(coord, "red")

        for i, coord in enumerate(self.edges):
            if i == len(self.edges) - 1:
                continue
            self._draw_number(coord.point1, i, "red")

    def _draw_number(self, coord: Coord, number: int, color: str) -> None:
        self._draw.text((coord.x, coord.y),
                        str(number),
                        fill=color,
                        font=self.font,
                        )

    def _draw_ellipse(self, coord: Coord, color: str) -> None:
        LINE_COLOR = color
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = (20 * CONST.ANTIALIAS_FACTOR) // 2
        self._draw.ellipse(
            (coord.x - SIZE, coord.y - SIZE, coord.x + SIZE, coord.y + SIZE),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )

    def _draw_edge(self, edge: Edge, color: str) -> None:
        LINE_COLOR = color
        LINE_WIDTH = 7 * CONST.ANTIALIAS_FACTOR
        self._draw.line(
            (edge.point1.x, edge.point1.y, edge.point2.x, edge.point2.y),
            fill=LINE_COLOR,
            width=LINE_WIDTH,
        )

    def _draw_point_debugg(self, x, y, color: str) -> None:
        self._draw.line((0, y, self.img.width, y),
                        fill=color,
                        )
        self._draw.line((x, 0, x, self.img.height),
                        fill=color,
                        )

    def _draw_cross(self, coord: Coord, color: str) -> None:
        LINE_COLOR = color
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