import generate
from image import Img
from CONST import Polygon, Coord
import CONST
import solver


def test():
    poly1 = Polygon([
        Coord(4000, 2000),
        Coord(4000, 4000),
        Coord(5000, 4000),
        Coord(5000, 2000)
    ])
    poly2 = Polygon([
        Coord(6000, 2000),
        Coord(6000, 4000),
        Coord(7000, 4000),
        Coord(7000, 2000)
    ])
    tour = [
        Coord(3000, 3000),
        Coord(3000, 9000),
        Coord(9000, 9000),
        Coord(9000, 3000),
        Coord(3000, 3000)
    ]
    obstacles = [poly1, poly2]
    img = Img([], obstacles, tour, CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)
    img.save("test_cut_two_obstacles")

    tour = solver.find_obstacle_plus_bypass(tour, obstacles)

    img = Img([], obstacles, tour, CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)
    img.save("test_around_two_obstacles")

    quit()




if __name__ == "__main__":
    test()
    

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
    polys = []
    polys.append(poly)
    problem_points = generate.find_obstacle(points, polys)

    # der Letze Punkt in der Tour der nicht das Polygon schneidet
    start = problem_points[0][0]

    # der erste Punkt in der Tour der wieder nicht schneidet
    end = problem_points[0][1]

    bypass_points = generate.bypass_polygon(poly, start, end)

    # Tour bis inkulisve start, dann neue pyPass Punkte ,
    # dann inklusive end bis zum ende der Tour
    points = points[:(points.index(start)+1)] + \
        bypass_points + points[points.index(end):]

    img = Img([poly], points, CONST.SCREEN_WIDTH, CONST.SCREEN_HEIGHT)
    img.save("testen_mit_bypass")
