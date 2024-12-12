import csv
from CONST import Coord, Polygon
import CONST


def write(points: list[tuple], name: str) -> None:
    with open(f"{CONST.INSTANCES_PRE}{name}.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["x", "y"], delimiter=";")
        writer.writeheader()  # Kopfzeile schreiben
        for coord in points:
            point = {"x": coord.x, "y": coord.y}
            writer.writerow(point)


def write_all_points(points: list[list[Coord]], name: str) -> None:
    with open(f"{CONST.INSTANCES_PRE}{name}allpoints.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["x", "y"], delimiter=";")
        writer.writeheader()  # Kopfzeile schreiben

        for i in range(CONST.AREA_COUNT):
            for j in range(CONST.CLUSTER_SIZE):
                point = {"x": points[i][j].x, "y": points[i][j].y}
                writer.writerow(point)


def read(name: str) -> list[Coord]:
    with open(f"{CONST.INSTANCES_PRE}{name}.csv", mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")
        coordinates_from_csv = [row for row in reader]

    areas = []
    for i in range(CONST.AREA_COUNT):
        cluster =[]
        for j in range(CONST.CLUSTER_SIZE):
            row = coordinates_from_csv[i * CONST.CLUSTER_SIZE + j]
            cluster.append(Coord(int(row["x"]), int(row["y"])))
        areas.append(cluster)
    return areas


def write_polygons(polygon_list: list[Polygon], name: str) -> None:
    with open(f"{CONST.INSTANCES_PRE}{name}polygonlist.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["x", "y"], delimiter=";")
        writer.writeheader()  # Kopfzeile schreiben

        for i in range(len(polygon_list)):
            for j in range(len(polygon_list[i].hull)):
                row = {"x":polygon_list[i].hull[j].x, "y":polygon_list[i].hull[j].y}
                writer.writerow(row)
            writer.writerow({"x": -1, "y": -1}) # fügt eine Reihe mit Koordinaten -1,-1 als Trennsymbol hinzu


def read_polygons(name: str) -> list[Polygon]:
    with open(f"{CONST.INSTANCES_PRE}{name}.csv", mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")
        coordinates_from_csv = [row for row in reader]
    
    polygon_list = []
    hull = []
    for i in range(len(coordinates_from_csv)):
        if int(coordinates_from_csv[i]["x"]) != -1:
            hull.append(Coord(int(coordinates_from_csv[i]["x"]), int(coordinates_from_csv[i]["y"])))
        else:
            polygon = Polygon(hull)
            polygon_list.append(polygon)
            hull = []
    return polygon_list