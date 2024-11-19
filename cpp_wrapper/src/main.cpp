#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <utility>
#include <iostream>
#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>
#include <random>
#include <cassert>

using namespace std;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

typedef std::pair<int, int> coord;
typedef std::vector<coord> tour;

double calculate_distance(const coord &a, const coord &b)
{
    return sqrt(pow(a.first - b.first, 2) + pow(a.second - b.second, 2));
}

double calculate_angle(const coord &p1, const coord &p2, const coord &p3)
{
    double vec_a_x = p2.first - p1.first, vec_a_y = p2.second - p1.second;
    double vec_b_x = p3.first - p2.first, vec_b_y = p3.second - p2.second;

    double mag_a = sqrt(vec_a_x * vec_a_x + vec_a_y * vec_a_y);
    double mag_b = sqrt(vec_b_x * vec_b_x + vec_b_y * vec_b_y);
    if (mag_a == 0 || mag_b == 0)
        return 0;

    double dot_product = vec_a_x * vec_b_x + vec_a_y * vec_b_y;
    double cos_theta = dot_product / (mag_a * mag_b);
    cos_theta = max(-1.0, min(1.0, cos_theta));

    return acos(cos_theta) * (180.0 / M_PI);
}

tour two_opt(tour tour)
{
    tour.pop_back(); // Entferne den letzten Punkt (Tour wird geschlossen)
    const double FACTOR = 0.9;
    bool improvement_found = true;

    while (improvement_found)
    {
        improvement_found = false;

        for (size_t i = 0; i < tour.size() - 1; ++i)
        {
            for (size_t j = i + 2; j < tour.size() - 2; ++j)
            {
                if (j == tour.size() - 1 && i == 0)
                    continue;

                double current_cost = (calculate_distance(tour[i], tour[i + 1]) +
                                       calculate_distance(tour[j], tour[j + 1])) *
                                          FACTOR +
                                      calculate_angle(tour[i], tour[i + 1], tour[i + 2]) +
                                      calculate_angle(tour[j], tour[j + 1], tour[j + 2]);

                double new_cost = (calculate_distance(tour[i], tour[j]) +
                                   calculate_distance(tour[i + 1], tour[j + 1])) *
                                      FACTOR +
                                  calculate_angle(tour[i], tour[j + 1], tour[i + 2]) +
                                  calculate_angle(tour[j], tour[i + 1], tour[j + 2]);

                if (new_cost < current_cost)
                {
                    reverse(tour.begin() + i + 1, tour.begin() + j + 1);
                    improvement_found = true;
                }
            }
        }
    }

    tour.push_back(tour[0]); // Schließe die Tour
    return tour;
}

tour farthest_insertion(tour &points)
{
    size_t n = points.size();
    vector<vector<double>> distance_matrix(n, vector<double>(n));

    for (size_t i = 0; i < n; ++i)
    {
        for (size_t j = 0; j < n; ++j)
        {
            distance_matrix[i][j] = calculate_distance(points[i], points[j]);
        }
    }

    // Initialisierung mit den zwei am weitesten entfernten Punkten
    double max_dist = 0;
    size_t start1 = 0, start2 = 1;
    for (size_t i = 0; i < n; ++i)
    {
        for (size_t j = i + 1; j < n; ++j)
        {
            if (distance_matrix[i][j] > max_dist)
            {
                max_dist = distance_matrix[i][j];
                start1 = i;
                start2 = j;
            }
        }
    }

    vector<coord> tour = {points[start1], points[start2], points[start1]};
    vector<bool> visited(n, false);
    visited[start1] = visited[start2] = true;

    while (tour.size() < n + 1)
    {
        double max_dist_to_tour = -1;
        size_t farthest_node = 0;

        for (size_t i = 0; i < n; ++i)
        {
            if (!visited[i])
            {
                double min_dist_to_tour = numeric_limits<double>::infinity();
                for (const auto &node : tour)
                {
                    min_dist_to_tour = min(min_dist_to_tour, calculate_distance(points[i], node));
                }
                if (min_dist_to_tour > max_dist_to_tour)
                {
                    max_dist_to_tour = min_dist_to_tour;
                    farthest_node = i;
                }
            }
        }

        double best_increase = numeric_limits<double>::infinity();
        size_t best_position = 0;
        for (size_t i = 0; i < tour.size() - 1; ++i)
        {
            double increase = calculate_distance(points[farthest_node], tour[i]) +
                              calculate_distance(points[farthest_node], tour[i + 1]) -
                              calculate_distance(tour[i], tour[i + 1]);

            if (increase < best_increase)
            {
                best_increase = increase;
                best_position = i;
            }
        }

        tour.insert(tour.begin() + best_position + 1, points[farthest_node]);
        visited[farthest_node] = true;
    }

    return tour;
}
tour ruin_and_recreate(tour tour, int iterations = 2000, double ruin_fraction = 0.3)
{
    auto best_tour = tour;
    double best_cost = calculate_distance(tour[0], tour.back());

    random_device rd;
    mt19937 gen(rd());

    for (int i = 0; i < iterations; ++i)
    {
        vector<coord> ruined_tour = tour;
        size_t num_remove = static_cast<size_t>(ruin_fraction * tour.size());
        for (size_t j = 0; j < num_remove; ++j)
        {
            ruined_tour.erase(ruined_tour.begin() + (gen() % ruined_tour.size()));
        }

        vector<coord> new_tour = ruined_tour;
        double new_cost = calculate_distance(new_tour[0], new_tour.back());

        if (new_cost < best_cost)
        {
            best_tour = new_tour;
            best_cost = new_cost;
        }
    }

    return best_tour;
}
namespace py = pybind11;

PYBIND11_MODULE(cpp_wrapper, m)
{
    m.def("two_opt", &two_opt);
    m.def("farthest_insertion", &farthest_insertion);
    m.def("ruin_and_recreate", &ruin_and_recreate);
    m.def("calculate_distance", &calculate_distance);
    m.def("calculate_angle", &calculate_angle);
}
