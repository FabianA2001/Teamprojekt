import generate
from image import Img
from CONST import Polygon, Coord
import CONST

if __name__ == "__main__":
    poly = Polygon([
        Coord(7074, 1517),
        Coord(7136, 1291),
        Coord(7972, 1105),
        Coord(8523, 1525),
        Coord(8367, 2002),
        Coord(7771, 2402),
        Coord(7270, 2162)
    ])
    points = [
        Coord(6500, 1000),
        Coord(8700, 1600),
        Coord(7900, 4000),
    ]

    img = Img([poly], points, CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)
    img.save("testen")

    # der Letze Punkt in der Tour der nicht das Polygon schneidet
    start = points[0]

    # der erste Punkt in der Tour der wieder nicht schneidet
    end = points[1]

    bypass_points = generate.bypass_polygon(poly, start, end)

    # Tour bis inkulisve start, dann neue pyPass Punkte ,
    # dann inklusive end bis zum ende der Tour
    points = points[:(points.index(start)+1)] + \
        bypass_points + points[points.index(end):]

    img = Img([poly], points, CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)
    img.save("testen_mit_bypass")
