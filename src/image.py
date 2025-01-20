from PIL import Image, ImageDraw, ImageFont
from CONST import Coord, Edge, Polygon
import file
import CONST
import random
import generate


class Img:
    def __init__(
        self,
        polygon_list: list[Polygon],
        obstacle_list: list[Polygon],
        points_in_route: list[Coord],
        height: int = CONST.SCREEN_HEIGHT,
        width: int = CONST.SCREEN_WIDTH
    ) -> None:
        self.polygon_list = polygon_list
        self.obstacle_list = obstacle_list
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

        self._draw_polygons()
        self._draw_obstacles(obstacle_list)
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

    def _draw_polygons(self) -> None:
        for i in range(len(self.polygon_list)):
            self._draw_hull(self.polygon_list[i].hull, self._random_color())
            """
            if i <= 2:
                self._draw_number(self.polygon_list[i].centroid, i, "pink")
            else:
                self._draw_number(self.polygon_list[i].centroid, i, "red")
            """

    def _draw_hull(self, points: list[Coord], color: str) -> None:
        hull = CONST.make_edges(points)
        for edge in hull:
            self._draw_edge(edge, color)

    
    def _draw_obstacles(self, obstacles: list[Polygon]) -> None:
        LINE_COLOR = "brown"
        for i in range(len(obstacles)):
            self._draw_hull(obstacles[i].hull, LINE_COLOR)
            self._draw_cross_in_polygon(obstacles[i], LINE_COLOR)
        return

    def _draw_cross_in_polygon(self, polygon: Polygon, color: str) -> None:
        min_x = min(x for x, y in polygon.hull)
        max_x = max(x for x, y in polygon.hull)
        min_y = min(y for x, y in polygon.hull)
        max_y = max(y for x, y in polygon.hull)
        edge1 = Edge(Coord(min_x, polygon.centroid.y), polygon.centroid)
        edge2 = Edge(Coord(max_x, polygon.centroid.y), polygon.centroid)
        edge3 = Edge(Coord(polygon.centroid.x, min_y), polygon.centroid)
        edge4 = Edge(Coord(polygon.centroid.x, max_y), polygon.centroid)
        edges_from_centroid = [edge1, edge2, edge3, edge4]
        polygon_hull = CONST.make_edges(polygon.hull)
        for edge_fc in edges_from_centroid:
            for edge_ph in polygon_hull:
                if generate.edge_intersection(edge_ph, edge_fc) != None:
                    point_on_hull = generate.edge_intersection(edge_ph, edge_fc)
            edge_to_hull = Edge(point_on_hull, polygon.centroid)
            self._draw_edge(edge_to_hull, color)
        return

    def _draw_route(self) -> None:
        for edge in self.edges:
            self._draw_edge(edge, "black")

        # for coord in self.points_in_route:
        #     self._draw_ellipse(coord, "red")

        for i, coord in enumerate(self.edges):
            if i == len(self.edges) - 1:
                continue
            self._draw_number(coord.point1, i, "red")

    def _draw_number(self, coord: Coord, number: int, color: str) -> None:
        self._draw.text((coord.x, coord.y),
                        str(number),
                        fill = color,
                        font = self.font,
                        )

    def _draw_ellipse(self, coord: Coord, color: str) -> None:
        LINE_COLOR = color
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = (20 * CONST.ANTIALIAS_FACTOR) // 2
        self._draw.ellipse(
            (coord.x - SIZE, coord.y - SIZE, coord.x + SIZE, coord.y + SIZE),
            fill = LINE_COLOR,
            width = LINE_WIDTH,
        )

    def _draw_edge(self, edge: Edge, color: str) -> None:
        LINE_COLOR = color
        LINE_WIDTH = 7 * CONST.ANTIALIAS_FACTOR
        self._draw.line(
            (edge.point1.x, edge.point1.y, edge.point2.x, edge.point2.y),
            fill = LINE_COLOR,
            width = LINE_WIDTH,
        )

    def _draw_point_debugg(self, x, y, color: str) -> None:
        self._draw.line((0, y, self.img.width, y),
                        fill = color,
                        )
        self._draw.line((x, 0, x, self.img.height),
                        fill = color,
                        )

    def _draw_cross(self, coord: Coord, color: str) -> None:
        LINE_COLOR = color
        LINE_WIDTH = 4 * CONST.ANTIALIAS_FACTOR
        SIZE = 20 // 2
        self._draw.line(
            (coord.x - SIZE, coord.y - SIZE, coord.x + SIZE, coord.y + SIZE),
            fill = LINE_COLOR,
            width = LINE_WIDTH,
        )
        self._draw.line(
            (coord.x - SIZE, coord.y + SIZE, coord.x + SIZE, coord.y - SIZE),
            fill = LINE_COLOR,
            width = LINE_WIDTH,
        )

    def _random_color(self):
        red = random.randint(0, 50)
        green = random.randint(50, 255)
        blue = random.randint(50, 255)
        color = "#{:02x}{:02x}{:02x}".format(red, green, blue)
        return color
