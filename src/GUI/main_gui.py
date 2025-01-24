import tkinter as tk
import random


class GraphEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")

        # Variablen für Knoten und Kanten
        self.nodes = []
        self.edges = []

        # Hauptlayout
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Buttons
        self.add_node_btn = tk.Button(
            self.frame, text="Add Node", command=self.add_node)
        self.add_edge_btn = tk.Button(
            self.frame, text="Add Edge", command=self.add_edge)
        self.clear_btn = tk.Button(
            self.frame, text="Clear Graph", command=self.clear_graph)

        self.add_node_btn.pack(side=tk.LEFT)
        self.add_edge_btn.pack(side=tk.LEFT)
        self.clear_btn.pack(side=tk.LEFT)

        # Canvas für Graph
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white")
        self.canvas.pack()

        # Log-Bereich
        self.log_list = tk.Listbox(self.root, height=10, width=80)
        self.log_list.pack()

    def log_message(self, message, error=False):
        """Fügt eine Nachricht in den Log-Bereich ein."""
        color = "red" if error else "black"
        self.log_list.insert(tk.END, message)
        self.log_list.itemconfig(tk.END, fg=color)

    def add_node(self):
        """Fügt einen neuen Knoten zum Graphen hinzu."""
        x, y = random.randint(50, 550), random.randint(50, 350)
        node_id = len(self.nodes)
        self.nodes.append({"id": node_id, "x": x, "y": y})
        self.canvas.create_oval(x - 10, y - 10, x + 10,
                                y + 10, fill="blue", tags=f"node_{node_id}")
        self.log_message(f"Node {node_id} added at ({x}, {y})")

    def add_edge(self):
        """Verbindet zwei zufällige Knoten mit einer Kante."""
        if len(self.nodes) < 2:
            self.log_message(
                "At least two nodes are required to add an edge!", error=True)
            return
        start, end = random.sample(self.nodes, 2)
        self.edges.append((start["id"], end["id"]))
        self.canvas.create_line(
            start["x"], start["y"], end["x"], end["y"], fill="gray", width=2)
        self.log_message(f"Edge added between Node {
                         start['id']} and Node {end['id']}")

    def clear_graph(self):
        """Löscht den Graphen."""
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.log_message("Graph cleared")


# Hauptprogramm
def main():
    root = tk.Tk()
    app = GraphEditorApp(root)
    root.mainloop()
