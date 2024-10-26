import math
import matplotlib.pyplot as plt



# vertices:                 list of (x, y)
# edges:                    list of (vertex_a, vertex_b, distance between vertex_a and vertex_b)
# edges_vertices_cosvalues: list of (edge, vertex_c, cosinus_value angle at vertex_c of triangle abc), while vertex_c is a possible vertex
#                           which would plit the edge in two new edges



def tctsp(vertices):

    def initialize_tour():
        max_distance = 0
        vertex_v = vertices[0]
        vertex_w = vertices[0]
        for i in range(len(vertices)):
            for j in range(i):
                distance = math.sqrt((vertices[i][0] - vertices[j][0]) ** 2 + (vertices[i][1] - vertices[j][1]) ** 2)
                if distance > max_distance:
                    max_distance = distance
                    vertex_v = vertices[i]
                    vertex_w = vertices[j]
        vertices.remove(vertex_v)
        vertices.remove(vertex_w)
        return [(vertex_v, vertex_w, max_distance), (vertex_w, vertex_v, max_distance)]


    def add_to_possible_edges(edges_to_add):
        for edge in edges_to_add:
            for vertex_c in vertices:
                vertex_a = edge[0]
                vertex_b = edge[1]
                edge_a = math.sqrt((vertex_c[0] - vertex_b[0]) ** 2 + (vertex_c[1] - vertex_b[1]) ** 2)
                edge_b = math.sqrt((vertex_c[0] - vertex_a[0]) ** 2 + (vertex_c[1] - vertex_a[1]) ** 2)
                edge_c = edge[2]
                cos_value = ((edge_c ** 2) - (edge_a ** 2) - (edge_b ** 2)) / (-2 * edge_a * edge_b) # law of cosinus
                edges_vertices_cosvalues.append((edge, vertex_c, cos_value))


    def get_best_edge():
        best_evc = edges_vertices_cosvalues[0]
        for evc in edges_vertices_cosvalues:
            if evc[2] < best_evc[2]:
                best_evc = evc
        return best_evc


    def add_edges_to_tour():
        while vertices:
            best_evc = get_best_edge()
            best_edge = best_evc[0]
            vertex_a = best_edge[0]
            vertex_b = best_edge[1]
            vertex_c = best_evc[1]
            edges.remove(best_edge)
            edges.append((vertex_a, vertex_c, math.sqrt((vertex_a[0] - vertex_c[0]) ** 2 + (vertex_a[1] - vertex_c[1]) ** 2)))
            edges.append((vertex_c, vertex_b, math.sqrt((vertex_c[0] - vertex_b[0]) ** 2 + (vertex_c[1] - vertex_b[1]) ** 2)))
            vertices.remove(vertex_c)
            edges_vertices_cosvalues[:] = [evc for evc in edges_vertices_cosvalues if evc[0] != best_edge and evc[1] != vertex_c] # removes, which contains old edge or vertex_c
            add_to_possible_edges([edges[len(edges) - 1], edges[len(edges) - 2]])


    def sort_edges():
        for i in range(len(edges)):
            for j in range(i, len(edges)):
                if edges[i - 1][1] == edges[j][0]:
                    break
            temp = edges[i]
            edges[i] = edges[j]
            edges[j] = temp


    def get_distance():
        distance = 0
        for edge in edges:
            distance += edge[2]
        return distance
    
        
    def get_angles_sum():
        radiant_sum = 0
        for i in range(len(edges)):
            vertex_a = edges[i - 1][0]
            vertex_b = edges[i][1]
            edge_a = edges[i][2]
            edge_b = edges[i - 1][2]
            edge_c_square = (vertex_a[0] - vertex_b[0]) ** 2 + (vertex_a[1] - vertex_b[1]) ** 2
            cos_gamma = (edge_c_square - (edge_a ** 2) - (edge_b ** 2)) / (-2 * edge_a * edge_b)    # law of cosinus
            radiant_gamma = math.acos(cos_gamma)
            radiant_sum += radiant_gamma
        angle_sum = 180 * len(edges) - radiant_sum * 180 / math.pi
        return angle_sum


    def plot_tour(distance, sum_turn_costs):
        edges_x = [edge[0][0] for edge in edges]
        edges_x.append(edges[0][0][0])
        edges_y = [edge[0][1] for edge in edges]
        edges_y.append(edges[0][0][1])
        vertices_x = [vertex[0] for vertex in copy_vertices]
        vertices_y = [vertex[1] for vertex in copy_vertices]
        plt.plot(edges_x, edges_y, color='black')
        plt.plot(vertices_x, vertices_y, 'o', color='red')
        plt.title('Distance: {:.2f} / Turn Costs: {:.2f}°'.format(distance, sum_turn_costs))
        plt.show()


    if not vertices:
        print('No vertices')
        return
    copy_vertices = vertices.copy()
    edges = initialize_tour()
    edges_vertices_cosvalues = []

    add_to_possible_edges(edges)
    add_edges_to_tour()
    sort_edges()
    sum_distance = get_distance()
    sum_angles = get_angles_sum()
    plot_tour(sum_distance, sum_angles)



def main():
    vertices = []
    for i in range(5):
        for j in range(5):
            vertices.append((i, j))
    tctsp(vertices)



if __name__ == "__main__":
    main()