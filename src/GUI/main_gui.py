import tkinter as tk
import random

import CONST


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
        self.draw_polygon_btn.pack(side='left')
        self.clear_btn.pack(side='left')
        self.remove_btn.pack(side='left')
        self.generate_btn.pack(side='left')

        self.lower_frame = tk.Frame(
            self.root)
        self.lower_frame.pack(pady=10)
        # Listbox erstellen
        self.listbox = tk.Listbox(self.lower_frame, font=(
            "Arial", 12), selectmode=tk.SINGLE, width=30)
        # sticky sorgt dafür, dass die Listbox den Frame füllt
        self.listbox.pack(side='left', fill="y", pady=3)
        # Ereignisbindung für die Auswahl
        self.listbox.bind("<<ListboxSelect>>", self.on_item_selected)

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

    def generate(self):
        self.drawing_mode = False
        self.draw_polygon_btn.config(state="disabled")
        self.remove_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.canvas.delete("all")

        polys_poly = []
        for poly in self.polygons:
            poly_coord: list[CONST.Coord] = []
            for point in poly:
                poly_coord.append(CONST.Coord(point[0], point[1]))
            polys_poly.append(CONST.Polygon(poly_coord))
        inst = Instanze("Blank", polys_poly)
        self.instes.append(inst)
        self.listbox.insert(tk.END, self.instes[0].name)

        self.instes.append(Instanze("zwei", poly=polys_poly[:2]))
        self.listbox.insert(tk.END, self.instes[1].name)

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
            inst = self.instes[selected_indices[0]]
            # Text des ausgewählten Elements
            self.canvas.delete("all")
            for poly in inst.polygone_tuple:
                self.draw_polygon(poly)

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


# Hauptprogramm
def main():
    app = GraphEditorApp()
    app.root.mainloop()
