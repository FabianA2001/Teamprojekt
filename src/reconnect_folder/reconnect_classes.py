from reconnect_folder import reconnect_functions as rf
import gurobipy as gb



class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def __iter__(self):
        return iter((self.x, self.y))
    

class Edge:
    def __init__(self, points, m):
        self.points = points
        self.distance = rf.get_distance(points[0], points[1])
        self.var = m.addVar(vtype=gb.GRB.BINARY)
    
    def __str__(self):
        return f"[{self.points[0]}, {self.points[1]}]"

    def __repr__(self):
        return f"[{self.points[0]}, {self.points[1]}]"