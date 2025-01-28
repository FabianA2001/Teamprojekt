import tkinter as tk
import random


class GraphEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Graph Editor")
        # Bildschirmbreite abrufen
        self.SCREEN_WIDTH = self.root.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.root.winfo_screenheight()

        # Hauptvariablen
        # Liste der Polygone (jeweils als Liste von Punkten)
        self.polygons = []
        self.drawing_mode = False  # Zeichnen aktivieren/deaktivieren
        self.current_polygon = []  # Punkte des aktuellen Polygons

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=0, column=0)
        # Buttons
        self.draw_polygon_btn = tk.Button(
            self.button_frame, text="Start Polygon", command=self.toggle_drawing_mode)
        self.clear_btn = tk.Button(
            self.button_frame, text="Clear Canvas", command=self.clear_canvas)

        self.draw_polygon_btn.pack(side='left')
        self.clear_btn.pack(side='left')

        # Canvas für Graph
        self.canvas = tk.Canvas(
            # self.root, width=20, height=400, bg="white")
            self.root, width=self.SCREEN_WIDTH*0.7, height=self.SCREEN_HEIGHT*0.9, bg="white")
        self.canvas.grid(row=1, column=1)

        # Frame für Listbox
        self.listbox_frame = tk.Frame(
            self.root, width=self.SCREEN_WIDTH*0.3, height=self.SCREEN_HEIGHT*0.9, bg="red")
        self.listbox_frame.grid(row=1, column=0, sticky="nsew")
        # Listbox erstellen
        self.listbox = tk.Listbox(self.listbox_frame, font=(
            "Arial", 12), selectmode=tk.SINGLE)
        # sticky sorgt dafür, dass die Listbox den Frame füllt
        self.listbox.grid(row=0, column=0, sticky="nsew")

        # Optional: Größe anpassen, damit der Frame und die Listbox den gewünschten Bereich ausfüllen
        self.listbox_frame.grid_rowconfigure(0, weight=1)
        self.listbox_frame.grid_columnconfigure(0, weight=1)

        # Elemente zur Listbox hinzufügen
        items = ["Apfel", "Banane", "Kirsche", "Orange",
                 "Pfirsich", "Trauben", "Wassermelone"]
        for item in items:
            self.listbox.insert(tk.END, item)

        # Ereignisbindung für die Auswahl
        self.listbox.bind("<<ListboxSelect>>", self.on_item_selected)

        # Canvas-Klick-Event binden
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def toggle_drawing_mode(self):
        """Aktiviert oder deaktiviert den Polygon-Zeichenmodus."""
        if not self.drawing_mode:
            self.draw_polygon_btn.config(text="Finish Polygon")
            self.current_polygon = []  # Leere Punkte für neues Polygon
        else:
            if len(self.current_polygon) <= 2:  # Nur gültig, wenn mehr als 2 Punkte
                return
            self.polygons.append(self.current_polygon)
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
            # Zeichne Punkt auf Canvas
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

    def clear_canvas(self):
        """Löscht den Canvas und alle gespeicherten Polygone."""
        self.canvas.delete("all")
        self.polygons.clear()
        self.current_polygon.clear()

    # Funktion, die ausgeführt wird, wenn ein Element angeklickt wird
    def on_item_selected(self, event):
        # Ausgewählte Elemente abrufen
        selected_indices = self.listbox.curselection()  # Index der ausgewählten Elemente
        if selected_indices:
            # Text des ausgewählten Elements
            selected_item = self.listbox.get(selected_indices[0])
            messagebox.showinfo("Element ausgewählt", f"Du hast '{
                                selected_item}' ausgewählt!")


# Hauptprogramm
def main():
    app = GraphEditorApp()
    app.root.mainloop()
