import tkinter as tk
import random


class GraphEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")

        # Hauptvariablen
        # Liste der Polygone (jeweils als Liste von Punkten)
        self.polygons = []
        self.drawing_mode = False  # Zeichnen aktivieren/deaktivieren
        self.current_polygon = []  # Punkte des aktuellen Polygons

        # Hauptlayout
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Buttons
        self.draw_polygon_btn = tk.Button(
            self.frame, text="Start Polygon", command=self.toggle_drawing_mode)
        self.clear_btn = tk.Button(
            self.frame, text="Clear Canvas", command=self.clear_canvas)

        self.draw_polygon_btn.pack(side=tk.LEFT)
        self.clear_btn.pack(side=tk.LEFT)

        # Canvas für Graph
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white")
        self.canvas.pack()

        # Log-Bereich
        self.log_list = tk.Listbox(self.root, height=10, width=80)
        self.log_list.pack()

        # Canvas-Klick-Event binden
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def toggle_drawing_mode(self):
        """Aktiviert oder deaktiviert den Polygon-Zeichenmodus."""
        if not self.drawing_mode:
            self.log_message(
                "Polygon drawing mode activated. Click to add points.")
            self.draw_polygon_btn.config(text="Finish Polygon")
            self.current_polygon = []  # Leere Punkte für neues Polygon
        else:
            if len(self.current_polygon) <= 2:  # Nur gültig, wenn mehr als 2 Punkte
                self.log_message(
                    "Polygon must have at least 3 points!", error=True)
                return
            self.polygons.append(self.current_polygon)
            self.log_message(f"Polygon finished with {
                len(self.current_polygon)} points.")
            self.canvas.create_polygon(
                self.current_polygon, outline="black", fill="", width=2)

            self.draw_polygon_btn.config(text="Start Polygon")
            self.current_polygon = []
        self.drawing_mode = not self.drawing_mode

    def on_canvas_click(self, event):
        """Fügt einen Punkt zum Polygon hinzu, wenn der Zeichenmodus aktiv ist."""
        if self.drawing_mode:
            x, y = event.x, event.y
            self.current_polygon.append((x, y))
            self.log_message(f"Point added at ({x}, {y}).")
            # Zeichne Punkt auf Canvas
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

    def clear_canvas(self):
        """Löscht den Canvas und alle gespeicherten Polygone."""
        self.canvas.delete("all")
        self.polygons.clear()
        self.current_polygon.clear()
        self.log_message("Canvas cleared.")

    def log_message(self, message, error=False):
        """Fügt eine Nachricht in den Log-Bereich ein."""
        color = "red" if error else "black"
        self.log_list.insert(tk.END, message)
        self.log_list.itemconfig(tk.END, fg=color)


# Hauptprogramm
def main():
    root = tk.Tk()
    app = GraphEditorApp(root)
    root.mainloop()
