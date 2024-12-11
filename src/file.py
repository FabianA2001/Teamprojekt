import csv
from CONST import Coord
import CONST


def write(points: list[Coord], name: str) -> None:
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


def read(name: str) -> list[list[Coord]]:
    with open(f"{CONST.INSTANCES_PRE}{name}.csv", mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")
        coordinates_from_csv = [row for row in reader]

    areas = []
    for i in range(CONST.AREA_COUNT):
        cluster = []
        for j in range(CONST.CLUSTER_SIZE):
            row = coordinates_from_csv[i * CONST.CLUSTER_SIZE + j]
            cluster.append(Coord(int(row["x"]), int(row["y"])))
        areas.append(cluster)
    return areas
