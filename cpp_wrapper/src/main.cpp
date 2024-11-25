
#define python 0

#if python
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#endif
#include <vector>
#include <utility>
#include <iostream>

#if python
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#endif

typedef std::pair<int, int> coord;
typedef std::vector<coord> tour;

tour two_opt(tour points)
{
    return points;
}

tour farthest_insertion(tour points)
{
    return points;
}
tour ruin_and_recreate(tour points)
{
    return points;
}

#if python
// namespace py = pybind11;
// PYBIND11_MODULE(cpp_wrapper, m)
// {
//     m.def("two_opt", &two_opt);
//     m.def("farthest_insertion", &farthest_insertion);
//     m.def("ruin_and_recreate", &ruin_and_recreate);
// }
#endif

int main()
{
    int x;
    std::cout << "test" << std::endl;
}