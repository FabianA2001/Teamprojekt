import tkinter as tk
import generate
import random

import CONST
import cpp_wrapper
import solver
from reconnect_folder import reconnect
# from Formatted_listbox import EditableFormattedListbox


class Instanze:
    def __init__(self, name: str, poly=[], points=[], obsticales=[]) -> None:
        self.name = name
        self.polygone_tuple = self.get_poly_tupel(poly)
        self.obsticales_tuple = self.get_poly_tupel(obsticales)
        self.points_tuple = self.get_points_tuple(points)

    def get_poly_tupel(self, polys: list[CONST.Polygon]):
        result = []
        for poly in polys:
            poly_list = []
            for point in poly.hull:
                poly_list.append(tuple(point))
            result.append(poly_list)
        return result

    def get_points_tuple(self, points):
        result = []
        for point in points:
            result.append(tuple(point))
        return result


class GraphEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Graph Editor")
        # Bildschirmbreite abrufen
        self.SCREEN_WIDTH = int(self.root.winfo_screenwidth() * 0.8)
        self.SCREEN_HEIGHT = int(self.root.winfo_screenheight() * 0.8)
        # self.SCREEN_WIDTH = 2000
        # self.SCREEN_HEIGHT = 1000

        # Hauptvariablen
        # Liste der Polygone (jeweils als Liste von Punkten)
        self.polygons = []
        self.drawing_mode = True  # Zeichnen aktivieren/deaktivieren
        self.current_polygon = []  # Punkte des aktuellen Polygons
        self.instes: list[Instanze] = []

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        # Buttons
        self.draw_polygon_btn = tk.Button(
            self.button_frame, text="Draw", command=self.draw)
        self.clear_btn = tk.Button(
            self.button_frame, text="Clear Canvas", command=self.clear_canvas)
        self.remove_btn = tk.Button(
            self.button_frame, text="Remove", command=self.remove)
        self.generate_btn = tk.Button(
            self.button_frame, text="Generate", command=self.generate)
        self.reset_btn = tk.Button(
            self.button_frame, text="Reset", command=self.reset)
        self.random_btn = tk.Button(
            self.button_frame, text="Random", command=self.random)

        self.draw_polygon_btn.pack(side='left')
        self.clear_btn.pack(side='left')
        self.remove_btn.pack(side='left')
        self.random_btn.pack(side='left')
        self.generate_btn.pack(side='left')
        self.reset_btn.pack(side='left')

        self.lower_frame = tk.Frame(
            self.root)
        self.lower_frame.pack(pady=10, side='left')

        self.listbox_frame = tk.Frame(self.lower_frame)
        self.listbox_frame.pack(side='left', fill="y", padx=4)
        # Listbox erstellen
        self.listbox = tk.Listbox(self.listbox_frame, font=(
            "Arial", 12), selectmode=tk.SINGLE, width=30)
        # sticky sorgt dafür, dass die Listbox den Frame füllt
        self.listbox.pack(fill="both", expand=True, pady=3)
        # Ereignisbindung für die Auswahl
        self.listbox.bind("<<ListboxSelect>>", self.on_item_selected)

        self.stats_frame = tk.Frame(self.listbox_frame)
        self.stats_frame.pack(fill="both", expand=True, pady=3)
#
        # self.dis_box = EditableFormattedListbox

        self.dis_box = tk.Listbox(self.stats_frame, font=(
            "Arial", 12), justify="right")
        self.dis_box.pack(fill="both", side="left",
                          expand=True, pady=3, padx=2)

        self.angle_box = tk.Listbox(self.stats_frame, font=(
            "Arial", 12), justify="right")
        # sticky sorgt dafür, dass die Listbox den Frame füllt
        self.angle_box.pack(fill="both", side="left",
                            expand=True, pady=3, padx=2)

        self.dis_box.insert(tk.END, "Distanze ")
        self.dis_box.insert(tk.END, "-"*30 + "  ")
        self.angle_box.insert(tk.END, "Winkel ")
        self.angle_box.insert(tk.END, "-" * 30 + "  ")

        # Canvas für Graph
        self.canvas = tk.Canvas(
            self.lower_frame, height=self.SCREEN_HEIGHT-self.button_frame.winfo_height(), width=self.SCREEN_WIDTH - self.listbox.winfo_width(), bg="white")
        self.canvas.pack(side='left')
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # # Elemente zur Listbox hinzufügen
        # items = ["Apfel", "Banane", "Kirsche", "Orange",
        #          "Pfirsich", "Trauben", "Wassermelone"]
        # for item in items:
        #     self.listbox.insert(tk.END, item)

    def draw_polygon(self, poly):
        self.canvas.create_polygon(
            poly, outline="black", fill="", width=2)

    def draw_obstacle(self, poly):
        self.canvas.create_polygon(
            poly, outline="red", fill="", width=2)

    def draw(self):
        """Aktiviert oder deaktiviert den Polygon-Zeichenmodus."""
        if not self.drawing_mode:
            return
        if len(self.current_polygon) <= 2:  # Nur gültig, wenn mehr als 2 Punkte
            self.show_popup("Error", "mehr als zwei Punkte")
            return
        self.polygons.append(self.current_polygon)
        self.draw_polygon(self.current_polygon)
        self.current_polygon = []

    def on_canvas_click(self, event):
        """Fügt einen Punkt zum Polygon hinzu, wenn der Zeichenmodus aktiv ist."""
        if self.drawing_mode:
            x, y = event.x, event.y
            self.current_polygon.append((x, y))
            # Zeichne Punkt auf Canvas
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

    def clear_canvas(self):
        """Löscht den Canvas und alle gespeicherten Polygone."""
        self.canvas.delete("all")
        self.polygons.clear()
        self.current_polygon.clear()

    def random(self):
        self.drawing_mode = False
        self.draw_polygon_btn.config(state="disabled")
        self.remove_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.generate_btn.config(state="disabled")
        self.random_btn.config(state="disabled")

        height = self.SCREEN_HEIGHT  # * CONST.ANTIALIAS_FACTOR
        width = self.SCREEN_WIDTH  # * CONST.ANTIALIAS_FACTOR
        print(self.SCREEN_HEIGHT, self.SCREEN_WIDTH)
        print(height, width)
        polygon_list: list[CONST.Polygon] = generate.generate_polygons(
            20, width, height, True)
        print("pol")
        for poly in polygon_list:
            print(poly.centroid)
        obstacle_list = generate.generate_polygons(
            4, width, height, False)
        print("obs")
        self.polygons = polygon_list

        self.instes.append(
            Instanze("Random", poly=polygon_list, obsticales=obstacle_list))
        print("app")
        self.listbox.insert(tk.END, self.instes[0].name)
        print("list")
        self.draw_instanze(self.instes[0])
        self.print_stats(0, 0)

    def generate(self):
        self.drawing_mode = False
        self.draw_polygon_btn.config(state="disabled")
        self.remove_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.generate_btn.config(state="disabled")
        self.random_btn.config(state="disabled")

        polygon_list = []
        for poly in self.polygons:
            poly_coord: list[CONST.Coord] = []
            for point in poly:
                poly_coord.append(CONST.Coord(point[0], point[1]))
            polygon_list.append(CONST.Polygon(poly_coord))

        self.instes.append(Instanze("Blank", polygon_list))
        self.listbox.insert(tk.END, self.instes[0].name)
        self.print_stats(0, 0)

        best_polygon_list = generate.find_best_polygon_list_2(polygon_list)
        self.instes.append(Instanze("überschneidung", poly=best_polygon_list))
        self.listbox.insert(tk.END, self.instes[-1].name)
        self.print_stats(0, 0)

        all_points = [i.hull.copy() for i in best_polygon_list]
        points = [poly.centroid for poly in best_polygon_list]
        for index, point in enumerate(points):
            all_points[index].append(point)

        points = cpp_wrapper.farthest_insertion([tuple(i) for i in points])
        points = CONST.to_coord(points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("farthest_insertion", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

        points = cpp_wrapper.ruin_and_recreate(
            [tuple(i) for i in points], 3000, 0.3, 1.2)
        points = CONST.to_coord(points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("ruin and recreate", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

        points = cpp_wrapper.two_opt([tuple(i) for i in points], 1.5)
        points = CONST.to_coord(points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("two opt", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

        points = solver.gurobi_solver(all_points, points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("Gurobi", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

        for _ in range(6):
            center_point = cpp_wrapper.get_point_with_max_angle(
                [tuple(i) for i in points])
            points = reconnect.optimize_the_closest(
                [tuple(i) for i in points], tuple(center_point))

        center_point = CONST.Coord(center_point[0], center_point[1])
        points = CONST.to_coord(points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("second run and recreate", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

        points = solver.move_points(polygon_list, points)
        dis, angle = solver.calculate_dis_angle(points)
        self.print_stats(dis, angle)
        self.instes.append(
            Instanze("move points", poly=polygon_list, points=points))
        self.listbox.insert(tk.END, self.instes[-1].name)

    def reset(self):
        self.canvas.delete("all")
        self.polygons.clear()
        self.drawing_mode = True  # Zeichnen aktivieren/deaktivieren
        self.current_polygon.clear()
        self.instes.clear()
        self.draw_polygon_btn.config(state="normal")
        self.remove_btn.config(state="normal")
        self.clear_btn.config(state="normal")
        self.generate_btn.config(state="normal")
        self.random_btn.config(state="normal")
        self.listbox.delete(0, tk.END)
        self.angle_box.delete(2, tk.END)
        self.dis_box.delete(2, tk.END)

    def remove(self):
        if len(self.polygons) == 0:
            return
        self.canvas.delete("all")
        del self.polygons[-1]
        for poly in self.polygons:
            self.draw_polygon(poly)

    # Funktion, die ausgeführt wird, wenn ein Element angeklickt wird
    def on_item_selected(self, event):
        # Ausgewählte Elemente abrufen
        selected_indices = self.listbox.curselection()  # Index der ausgewählten Elemente
        if selected_indices:
            index = selected_indices[0]
            inst = self.instes[index]
            # Text des ausgewählten Elements
            self.canvas.delete("all")
            self.draw_instanze(inst)
            self.dis_box.selection_set(index + 2)
            self.angle_box.selection_set(index + 2)

    def draw_instanze(self, inst: Instanze) -> None:
        for poly in inst.polygone_tuple:
            self.draw_polygon(poly)

        for obs in inst.obsticales_tuple:
            self.draw_polygon(obs)

        if len(inst.points_tuple) >= 3:
            self.canvas.create_polygon(
                inst.points_tuple, outline="red", fill="", width=2)

    # Function to show the popup

    def show_popup(self, titel, text):
        # Fenstergröße ermitteln
        window_width = 300
        window_height = 150
        # Bildschirmgröße ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Berechne die Position, um das Fenster in der Mitte zu platzieren
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Create a popup window
        popup = tk.Toplevel()
        popup.title(titel)
        # Fenster positionieren
        popup.geometry(f'{window_width}x{
                       window_height}+{position_right}+{position_top}')

        # Add a label in the popup window
        label = tk.Label(popup, text=text)
        label.pack(pady=20)

        # Add a button to close the popup
        button = tk.Button(popup, text="Close", command=popup.destroy)
        button.pack()

    def print_stats(self, dis: float, angle: float):
        self.dis_box.insert(tk.END, f" {dis:.2f}")
        self.angle_box.insert(tk.END, f" {angle:.2f}")


# Hauptprogramm
def main():
    app = GraphEditorApp()
    app.root.mainloop()
