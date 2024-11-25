
#define python 0

#if python
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#endif
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

#if python
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)
#endif

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

std::vector<double> calculate_turn_angles(const tour &path)
{
    std::vector<double> angles;

    // Schleife von Index 1 bis path.size() - 2, da drei Punkte benötigt werden
    for (size_t i = 1; i < path.size() - 1; ++i)
    {
        const coord &p1 = path[i - 1]; // Vorheriger Punkt
        const coord &p2 = path[i];     // Aktueller Punkt
        const coord &p3 = path[i + 1]; // Nächster Punkt

        // Berechne den Winkel zwischen den Punkten und füge ihn zur Liste hinzu
        double angle = calculate_angle(p1, p2, p3); // Annahme: `calculate_angle` existiert
        angles.push_back(angle);
    }

    return angles;
}
double calculate_tour_distance(const tour &tour)
{
    double total_distance = 0.0;

    for (size_t i = 0; i < tour.size(); ++i)
    {
        const coord &current = tour[i];
        const coord &next = tour[(i + 1) % tour.size()];     // Zyklisch zur ersten Stadt
        total_distance += calculate_distance(current, next); // Annahme: Funktion existiert
    }

    return total_distance;
}
void select_random_elements(const tour &tour, ::tour &to_remove, size_t num_remove)
{
    // Kopiere die Tour, um sie zu mischen
    ::tour shuffled_tour = tour;

    // Zufälliges Mischen der Tour
    std::random_device rd;
    std::mt19937 gen(rd());
    std::shuffle(shuffled_tour.begin(), shuffled_tour.end(), gen);

    // Wähle die ersten `num_remove` Elemente
    to_remove.assign(shuffled_tour.begin(), shuffled_tour.begin() + num_remove);
}

tuple<tour, tour> ruin(::tour tour, double ruin_fraction = 0.3)
{
    std::cout << "ruin";
    size_t n = tour.size();
    coord first_city = tour.at(0);
    size_t num_remove = static_cast<size_t>(n * ruin_fraction);
    ::tour to_remove;
    ::tour new_tour = tour;
    // Zufällige Auswahl der zu entfernenden Städte
    std::random_device rd;
    std::mt19937 gen(rd());
    select_random_elements(tour, to_remove, num_remove);

    // Sicherstellen, dass die Startstadt nicht entfernt wird
    while (std::find(to_remove.begin(), to_remove.end(), first_city) != to_remove.end())
    {
        to_remove.clear();
        select_random_elements(tour, to_remove, num_remove);
    }
    new_tour.erase(std::remove_if(new_tour.begin(), new_tour.end(),
                                  [&](const coord &city)
                                  {
                                      return std::find(to_remove.begin(), to_remove.end(), city) != to_remove.end();
                                  }),
                   new_tour.end());

    return {new_tour, to_remove};
}

tour recreate(tour tour, const ::tour &removed_cities)
{
    std::cout << "recreate";
    for (const auto &city : removed_cities)
    {
        size_t best_position = 0;
        double best_cost = std::numeric_limits<double>::infinity();

        for (size_t i = 1; i < tour.size(); ++i)
        {
            // Erstelle eine neue Tour mit der aktuellen Stadt an Position i
            ::tour new_tour = tour;
            new_tour.insert(new_tour.begin() + i, city);

            // Kosten der neuen Tour berechnen
            std::vector<double> angles = calculate_turn_angles(new_tour); // Liste von Winkeln
            double cost = 0.0;
            for (const double angle : angles)
            {
                cost += angle; // Summiere alle Winkel auf
            }

            // Beste Position aktualisieren
            if (cost < best_cost)
            {
                best_cost = cost;
                best_position = i;
            }
        }

        // Stadt an der besten Position einfügen
        tour.insert(tour.begin() + best_position, city);
    }

    return tour;
}

tour ruin_and_recreate(::tour tour, int iterations, double ruin_fraction, double distance_mul)
{
    std::cout << "ruin and recreate";
    // Beste Tour initialisieren
    ::tour best_tour = tour;
    double best_angles_cost = std::accumulate(calculate_turn_angles(tour).begin(), calculate_turn_angles(tour).end(), 0.0);
    double best_distance_cost = calculate_tour_distance(tour);

    for (int i = 0; i < iterations; ++i)
    {
        // Ruin-Phase: Entferne zufällig Städte aus der Tour
        auto [ruined_tour, removed_cities] = ruin(best_tour, ruin_fraction);

        // Recreate-Phase: Füge die entfernten Städte wieder ein
        ::tour new_tour = recreate(ruined_tour, removed_cities);

        // Kosten der neuen Tour berechnen
        double new_angles_cost = std::accumulate(calculate_turn_angles(new_tour).begin(), calculate_turn_angles(new_tour).end(), 0.0);
        double new_distance_cost = calculate_tour_distance(new_tour);

        // Aktualisiere die beste Lösung, falls die neue Tour besser ist
        if (new_angles_cost < best_angles_cost && new_distance_cost < distance_mul * best_distance_cost)
        {
            if (new_distance_cost < best_distance_cost)
            {
                best_distance_cost = new_distance_cost;
            }
            best_tour = new_tour;
            best_angles_cost = new_angles_cost;
        }
    }

    return best_tour;
}

tour ruin_and_recreate1(tour tour, int iterations = 2000, double ruin_fraction = 0.3)
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

#if python
namespace py = pybind11;
PYBIND11_MODULE(cpp_wrapper, m)
{
    m.def("two_opt", &two_opt);
    m.def("farthest_insertion", &farthest_insertion);
    m.def("ruin_and_recreate", &ruin_and_recreate);
    m.def("two_opt", &two_opt);
    m.def("farthest_insertion", &farthest_insertion);
    m.def("ruin_and_recreate", &ruin_and_recreate);
    m.def("ruin_and_recreate1", &ruin_and_recreate1);
    m.def("calculate_distance", &calculate_distance);
    m.def("calculate_angle", &calculate_angle);
    m.def("ruin", &ruin);
    m.def("calculate_turn_angles", &calculate_turn_angles);
    m.def("recreate", &recreate);
    m.def("calculate_tour_distance", &calculate_tour_distance);
}
#endif

int main()
{
    tour points = {{1, 2}, {1, 4}};
}
