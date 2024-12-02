import cpp_wrapper
from CONST import Coord

x = [Coord(1, 2), Coord(3, 4)]
print(cpp_wrapper.two_opt([tuple(i) for i in x]))
print(cpp_wrapper.farthest_insertion([tuple(i) for i in x]))
print(cpp_wrapper.ruin_and_recreate(
    [(int(i.x), int(i.y)) for i in x], 3000, 0.3))
