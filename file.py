import csv
from CONST import Coord


def write(points: list[Coord], name: str) -> None:
    with open(f"{name}.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["x", "y"], delimiter=";")
        writer.writeheader()  # Kopfzeile schreiben
        for coord in points:
            point = {"x": coord.x, "y": coord.y}
            writer.writerow(point)


def read(name: str) -> list[Coord]:
    with open(f"{name}.csv", mode="r") as file:
        reader = csv.DictReader(file, delimiter=";")
        coordinates_from_csv = [row for row in reader]

    result = []
    for row in coordinates_from_csv:
        result.append(Coord(int(row["x"]), int(row["y"])))

    return result
