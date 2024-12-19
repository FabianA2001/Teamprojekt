
#define python 1

#if python
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#endif

#define _USE_MATH_DEFINES
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#include <vector>
#include <utility>
#include <iostream>
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
typedef std::vector<coord> area;

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

coord get_closest_point(const area _area)
{
    coord sum(0, 0);
    for (const auto &point : _area)
    {
        sum.first += point.first;
        sum.second += point.second;
    }
    coord mid(double(sum.first) / _area.size(), double(sum.second) / _area.size());
    if (_area.empty())
    {
        throw invalid_argument("Area darf nicht leer sein");
    }
    coord closest = _area[0];
    for (int i = 1; i < _area.size(); ++i)
    {
        if (calculate_distance(mid, _area[i]) < calculate_distance(mid, closest))
        {
            closest = _area[i];
        }
    }
    return closest;
}

tour get_midpoints_from_areas(vector<area> areas)
{
    tour _tour;
    for (const auto &_area : areas)
    {
        _tour.push_back(get_closest_point(_area));
    }
    return _tour;
}

tour two_opt_path(tour path, double FACTOR)
{
    bool improvement_found = true;

    // Keine Rückverbindung notwendig, da es ein Pfad ist
    while (improvement_found)
    {
        improvement_found = false;

        for (size_t i = 0; i < path.size() - 2; ++i) // Bis zum vorletzten Element
        {
            for (size_t j = i + 2; j < path.size(); ++j) // Überprüfe Paare ohne Endpunkte
            {
                // Berechne die Kosten der aktuellen Kanten
                double current_cost = (calculate_distance(path[i], path[i + 1]) +
                                       calculate_distance(path[j], path[j - 1])) *
                                          FACTOR +
                                      calculate_angle(path[i], path[i + 1], path[i + 2]) +
                                      calculate_angle(path[j], path[j - 1], path[j - 2]);

                // Berechne die Kosten der neuen Kanten nach einem Tausch
                double new_cost = (calculate_distance(path[i], path[j]) +
                                   calculate_distance(path[i + 1], path[j - 1])) *
                                      FACTOR +
                                  calculate_angle(path[i], path[j], path[i + 1]) +
                                  calculate_angle(path[j], path[i + 1], path[j - 1]);

                // Wenn der Tausch die Gesamtkosten verringert, führe ihn durch
                if (new_cost < current_cost)
                {
                    reverse(path.begin() + i + 1, path.begin() + j); // Drehe den Teilbereich um
                    improvement_found = true;
                }
            }
        }
    }

    return path;
}
tour two_opt(tour tour_p, double FACTOR)
{
    tour_p.pop_back(); // Entferne den letzten Punkt (Tour wird geschlossen)

    tour_p = two_opt_path(tour_p, FACTOR);

    tour_p.push_back(tour_p[0]); // Schließe die Tour
    return tour_p;
}
vector<tour> get_quarter_tours(tour areas)
{
    tour tour_up_l;
    tour tour_up_r;
    tour tour_do_l;
    tour tour_do_r;
    for (coord cord : areas)
    {
        if (cord.first < 10000 and cord.second < 10000)
        {
            tour_do_l.push_back(cord);
        }
        else if (cord.first < 10000 and cord.second >= 10000)
        {
            tour_up_l.push_back(cord);
        }
        else if (cord.first >= 10000 and cord.second >= 10000)
        {
            tour_up_r.push_back(cord);
        }
        else if (cord.first >= 10000 and cord.second < 10000)
        {
            tour_do_r.push_back(cord);
        }
    }
    return {tour_do_l, tour_do_r, tour_up_l, tour_up_r};
}

tour shortest_path(tour points, coord start, coord end)
{
    // coord start = start;
    // coord end = end;

    // Überprüfe, ob Start und Ende bereits in der Liste sind
    // if (std::find(points.begin(), points.end(), start) == points.end())
    points.push_back(start);
    // if (std::find(points.begin(), points.end(), end) == points.end())
    points.push_back(end);

    size_t n = points.size();

    // Erstelle die Distanzmatrix
    vector<vector<double>> distance_matrix(n, vector<double>(n));
    for (size_t i = 0; i < n; ++i)
    {
        for (size_t j = 0; j < n; ++j)
        {
            distance_matrix[i][j] = calculate_distance(points[i], points[j]);
        }
    }

    // Initialisiere Tour mit Start- und Endpunkten
    vector<coord> restour = {start, end};
    vector<bool> visited(n, false);

    // Markiere Start und Ende als besucht
    visited[n - 2] = true; // Start
    visited[n - 1] = true; // Endpunkt

    while (restour.size() < n)
    {
        size_t farthest_node = -1;
        double max_dist_to_tour = -1;

        // Finde den am weitesten entfernten Punkt von der aktuellen Tour
        for (size_t i = 0; i < n; ++i)
        {
            if (!visited[i])
            {
                double min_dist_to_tour = numeric_limits<double>::infinity();
                for (const auto &node : restour)
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

        // Finde die beste Position, um den Punkt in die Tour einzufügen
        size_t best_position = -1;
        double best_increase = numeric_limits<double>::infinity();
        for (size_t i = 0; i < restour.size() - 1; ++i)
        {
            double increase = calculate_distance(points[farthest_node], restour[i]) +
                              calculate_distance(points[farthest_node], restour[i + 1]) -
                              calculate_distance(restour[i], restour[i + 1]);

            if (increase < best_increase)
            {
                best_increase = increase;
                best_position = i;
            }
        }

        // Füge den Punkt in die Tour ein
        restour.insert(restour.begin() + best_position + 1, points[farthest_node]);
        visited[farthest_node] = true;
    }
    // if (start.first = 5000)
    // {
    //     restour = two_opt_path(restour, 0.0);
    // }

    return restour;
}

tour small_tours(tour points)
{
    vector<tour> tours = get_quarter_tours(points);
    tour tour_do_l = tours[0];
    tour tour_do_r = tours[1];
    tour tour_up_l = tours[2];
    tour tour_up_r = tours[3];

    tour_do_l = shortest_path(tour_do_l, {5000, 10000}, {10000, 5000});
    tour_do_r = shortest_path(tour_do_r, {10000, 5000}, {15000, 10000});
    tour_up_l = shortest_path(tour_up_l, {10000, 15000}, {5000, 10000});
    tour_up_r = shortest_path(tour_up_r, {15000, 10000}, {10000, 15000});

    tour result;
    size_t n1 = tour_do_l.size();
    for (size_t i = 1; i < n1 - 1; i++)
    {
        result.push_back(tour_do_l[i]);
    }
    size_t n2 = tour_do_r.size();
    for (size_t i = 1; i < n2 - 1; i++)
    {
        result.push_back(tour_do_r[i]);
    }
    size_t n3 = tour_up_r.size();
    for (size_t i = 1; i < n3 - 1; i++)
    {
        result.push_back(tour_up_r[i]);
    }
    size_t n4 = tour_up_l.size();
    for (size_t i = 1; i < n4 - 1; i++)
    {
        result.push_back(tour_up_l[i]);
    }
    result.push_back(result[0]);
    return result;
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
        double angle = calculate_angle(p1, p2, p3);

        angles.push_back(angle);
    }
    double new_angles_cost = 0.0;

    for (double angle : angles)
    {
        new_angles_cost += angle;
    }
    // std::cout << new_angles_cost << "\n";
    return angles;
}

bool istPunktImKreis(double punktX, double punktY, double kreisX, double kreisY, double radius)
{
    // Berechne den Abstand zwischen dem Punkt und dem Mittelpunkt des Kreises
    double abstand = std::sqrt(std::pow(punktX - kreisX, 2) + std::pow(punktY - kreisY, 2));
    return abstand <= radius;
}

pair<tour, coord> radius_tour(vector<tour> all_points, tour points, double radius)
{
    vector<double> angles = calculate_turn_angles(points);
    double max = 0.0;
    int position;
    for (int i = 0; i < angles.size(); i++)
    {
        if (angles[i] > max)
        {
            max = angles[i];
            position = i;
        }
    }
    coord center_coord = points[(position + 1) % points.size()];
    tour new_tour;
    vector<tour> radius_areas;
    for (tour area : all_points)
    {
        for (coord cord : area)
        {
            if (istPunktImKreis(cord.first, cord.second, center_coord.first, center_coord.second, radius))
            {
                radius_areas.push_back(area);
                break;
            }
        }
    }
    new_tour = get_midpoints_from_areas(radius_areas);
    new_tour = farthest_insertion(new_tour);
    return {new_tour, center_coord};
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
    // std::cout << "ruin";
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
    // std::cout << "recreate";
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
    // std::cout << "ruin and recreate";
    //  Beste Tour initialisierendouble
    std::vector<double> angles = calculate_turn_angles(tour);
    double best_angles_cost = 0.0;

    for (double angle : angles)
    {
        best_angles_cost += angle;
    }

    ::tour best_tour = tour;

    double best_distance_cost = calculate_tour_distance(tour);

    for (int i = 0; i < iterations; ++i)
    {
        // Ruin-Phase: Entferne zufällig Städte aus der Tour
        auto [ruined_tour, removed_cities] = ruin(best_tour, ruin_fraction);

        // Recreate-Phase: Füge die entfernten Städte wieder ein
        ::tour new_tour = recreate(ruined_tour, removed_cities);

        // Kosten der neuen Tour berechnen
        std::vector<double> angles = calculate_turn_angles(new_tour);
        double new_angles_cost = 0.0;

        for (double angle : angles)
        {
            new_angles_cost += angle;
        }

        double new_distance_cost = calculate_tour_distance(new_tour);

        // Aktualisiere die beste Lösung, falls die neue Tour besser ist
        // std::cout << "a " << new_angles_cost << " " << best_angles_cost << "\n";
        // std::cout << "d " << new_distance_cost << " " << best_distance_cost << "\n";
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
    m.def("get_midpoints_from_areas", &get_midpoints_from_areas);
    m.def("small_tours", &small_tours);
    m.def("get_quarter_tours", &get_quarter_tours);
    m.def("shortest_path", &shortest_path);
    m.def("radius_tour", &radius_tour);
}
#endif

int main()
{
    vector<tour> all_points = {{{7163, 9837}, {7531, 9647}, {7820, 9955}, {7791, 10539}, {7473, 10486}, {7194, 10042}, {7170, 9893}},
                               {{10025, 14125}, {10276, 13573}, {10821, 13968}, {10741, 14256}, {10511, 14473}, {10063, 14278}},
                               {{17492, 9689}, {17594, 9068}, {18069, 8899}, {18324, 9094}, {18311, 9622}, {17852, 9774}},
                               {{6351, 7925}, {6414, 7524}, {6715, 7488}, {6884, 8040}, {6926, 8253}, {6691, 8283}},
                               {{14362, 6191}, {14910, 5852}, {15092, 6472}, {14656, 6734}, {14479, 6556}},
                               {{6672, 9045}, {7059, 8768}, {7335, 9286}, {7467, 9628}, {6951, 9600}, {6726, 9464}},
                               {{13070, 7150}, {13850, 7248}, {13750, 7942}, {13327, 7871}, {13088, 7801}},
                               {{13350, 8190}, {13482, 8076}, {13877, 7847}, {14163, 7885}, {14190, 8781}, {13470, 8784}},
                               {{8009, 14696}, {8084, 14683}, {8702, 14702}, {8978, 15073}, {8593, 15418}, {8033, 15340}},
                               {{11798, 7535}, {11909, 7060}, {12069, 6980}, {12608, 6889}, {12732, 7267}, {12696, 7361}, {12219, 7796}, {11959, 7764}},
                               {{4992, 10065}, {5076, 9363}, {5719, 9272}, {5853, 10238}},
                               {{2382, 6214}, {2486, 5726}, {2632, 5784}, {3160, 6048}, {3322, 6332}, {3069, 6437}},
                               {{14275, 4839}, {14414, 4408}, {15193, 4649}, {15226, 5124}, {14315, 5284}},
                               {{10329, 16444}, {11081, 16327}, {11230, 16791}, {11240, 17144}, {10772, 17304}, {10660, 17158}, {10599, 17048}},
                               {{16026, 14255}, {16665, 14005}, {16723, 13989}, {16931, 14088}, {16765, 14856}, {16598, 14841}, {16257, 14685}},
                               {{10605, 14605}, {10898, 14300}, {11332, 14073}, {11517, 14425}, {11476, 14458}, {11190, 14602}},
                               {{13895, 11101}, {13960, 10920}, {14568, 10836}, {14784, 11091}, {14852, 11269}, {14452, 11425}, {13944, 11233}},
                               {{11413, 6659}, {11872, 6290}, {12382, 7055}, {11786, 7213}},
                               {{17357, 14010}, {17747, 13671}, {18038, 13625}, {18199, 14293}, {17368, 14351}},
                               {{6395, 7207}, {6878, 7209}, {7016, 7893}, {6936, 8038}, {6644, 8090}, {6419, 7976}},
                               {{8899, 10056}, {8995, 9558}, {9604, 9542}, {9779, 9573}, {9815, 10039}, {9173, 10113}},
                               {{11256, 15109}, {11345, 14320}, {11643, 14456}, {12239, 14997}, {12079, 15182}, {11454, 15253}},
                               {{10688, 10771}, {10728, 10120}, {11234, 10109}, {11491, 10363}, {11465, 11021}, {11391, 11029}},
                               {{2035, 15865}, {2039, 15563}, {2095, 15146}, {2541, 15450}, {2299, 15895}, {2182, 15970}},
                               {{5040, 12191}, {5094, 11604}, {5901, 11760}, {5879, 11855}, {5482, 12521}},
                               {{5882, 5789}, {6530, 5506}, {6620, 5511}, {6734, 6290}, {6266, 6307}, {6050, 6148}},
                               {{12090, 8866}, {12104, 8353}, {12517, 8159}, {12760, 8285}, {12866, 8419}, {12486, 8739}, {12226, 8904}},
                               {{8412, 10102}, {8539, 10084}, {8698, 10201}, {9116, 10833}, {8743, 10829}, {8469, 10654}},
                               {{14855, 4902}, {14990, 4725}, {15725, 4587}, {15805, 5006}, {15747, 5331}, {15316, 5496}, {15006, 5509}},
                               {{10119, 3576}, {10253, 3121}, {10379, 2848}, {10704, 3174}, {10628, 3658}},
                               {{14158, 7523}, {14685, 6954}, {14822, 7288}, {14749, 7717}, {14489, 7816}, {14299, 7865}},
                               {{4977, 13896}, {5059, 13764}, {5582, 13922}, {5699, 14065}, {5458, 14443}, {5090, 14661}},
                               {{8084, 11811}, {8389, 11930}, {8467, 12108}, {8341, 12631}, {8166, 12715}, {8103, 12669}, {8094, 12420}},
                               {{1733, 3203}, {1816, 2785}, {1981, 2458}, {2532, 2478}, {2598, 2736}, {2255, 3115}, {1940, 3295}},
                               {{2594, 17121}, {3035, 17101}, {3383, 17325}, {3395, 18056}, {3275, 18008}, {2602, 17676}},
                               {{1820, 9025}, {2146, 8602}, {2275, 8631}, {2553, 8775}, {2701, 8983}, {2611, 9259}, {2331, 9277}},
                               {{4866, 13102}, {4900, 12850}, {5444, 12495}, {5768, 13163}, {5720, 13390}, {5125, 13397}},
                               {{9937, 3428}, {10219, 3007}, {10796, 3062}, {10933, 3546}, {10718, 3647}},
                               {{8211, 17003}, {8697, 16715}, {8702, 16720}, {9109, 17242}, {8794, 17565}, {8267, 17503}, {8225, 17246}},
                               {{5447, 16433}, {5742, 15888}, {6236, 16136}, {6165, 16569}, {6104, 16730}, {5933, 16825}},
                               {{9133, 12140}, {9162, 11560}, {10068, 11271}, {9773, 12190}, {9422, 12190}},
                               {{2020, 9265}, {2310, 8899}, {2841, 8656}, {2875, 8967}, {2144, 9440}, {2056, 9392}},
                               {{5194, 4249}, {5354, 3894}, {5921, 3324}, {6003, 3552}, {6131, 4086}},
                               {{13296, 5400}, {13739, 5569}, {13891, 5885}, {13757, 6287}, {13585, 6180}},
                               {{2975, 1934}, {3546, 1932}, {3805, 2387}, {3453, 2831}, {3395, 2893}, {3132, 2903}},
                               {{13768, 5505}, {14363, 5343}, {14692, 5448}, {14681, 5997}, {14550, 6076}, {14146, 5991}},
                               {{14555, 16898}, {14559, 16402}, {15068, 16153}, {15341, 16650}, {15323, 16731}},
                               {{5778, 4113}, {5793, 3832}, {5826, 3754}, {6304, 3414}, {6551, 3458}, {6558, 4051}, {5873, 4133}},
                               {{16370, 14393}, {16432, 13646}, {17355, 14021}, {17025, 14319}},
                               {{14436, 2995}, {14510, 2521}, {14968, 2480}, {15265, 2905}, {14659, 3049}},
                               {{5348, 15004}, {5904, 14992}, {6107, 15554}, {6033, 15790}, {5444, 15637}},
                               {{14110, 5913}, {14138, 5825}, {14515, 5862}, {14829, 5991}, {14791, 6155}, {14445, 6372}, {14204, 6322}},
                               {{12031, 7038}, {12094, 6886}, {12983, 6858}, {12935, 7107}, {12735, 7616}, {12340, 7737}},
                               {{13922, 10793}, {14031, 10607}, {14695, 10694}, {14373, 11416}, {14030, 11241}, {14002, 11160}},
                               {{16720, 4336}, {16736, 4325}, {16845, 4330}, {17438, 4401}, {17190, 4870}, {16891, 5297}, {16758, 4612}},
                               {{8257, 15530}, {8325, 14938}, {8543, 14824}, {8967, 14849}, {8996, 14890}, {8868, 15532}},
                               {{3179, 3573}, {3576, 3387}, {3768, 3407}, {3838, 3840}, {3441, 4184}},
                               {{2189, 6427}, {2208, 5926}, {2504, 5664}, {2943, 5486}, {2871, 6439}},
                               {{14536, 5616}, {14538, 5592}, {14869, 5168}, {15115, 5850}, {14810, 5921}, {14618, 5821}},
                               {{16893, 11069}, {17050, 10861}, {17557, 10645}, {17680, 10948}, {17679, 11156}, {17578, 11492}}};
    tour points = {{915, 3759}, {3440, 675}, {1141, 1864}, {2759, 3850}, {2007, 223}, {760, 130}, {527, 964}, {3046, 3001}, {1190, 1005}, {1875, 1780}, {3047, 599}, {2310, 3239}, {1959, 2624}, {2768, 3116}, {1701, 408}, {129, 2746}, {3627, 2663}, {435, 3874}, {819, 3155}, {285, 1302}, {2589, 2566}, {2225, 2097}, {2522, 841}, {3571, 2398}, {1780, 2784}, {456, 2748}, {2551, 3786}, {1212, 2764}, {2852, 2775}, {3510, 1174}, {188, 3545}, {898, 2969}, {948, 1061}, {3658, 1548}, {3678, 1319}, {585, 1196}, {227, 531}, {409, 2335}, {852, 865}, {420, 695}, {3515, 1976}, {2234, 3020}, {830, 2387}, {3121, 2046}, {1701, 2493}, {2860, 2025}, {264, 1522}, {860, 2134}, {3196, 3294}, {1086, 3069}};
    // points = ruin_and_recreate(points, 3000, 0.3, 1.2);
    points = small_tours(points);
}
