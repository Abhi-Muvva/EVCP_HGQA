import matplotlib.pyplot as plt
import random
from prettytable import PrettyTable
import pandas as pd

# Function to generate random co-ordinates
def generate_random_coordinates(X_MIN, X_MAX, Y_MIN, Y_MAX, n):
    coordinates = [(random.uniform(X_MIN, X_MAX), random.uniform(Y_MIN, Y_MAX)) for _ in range(n)]
    return coordinates


# This function divides the graph in to grids based on the number of qubits given
def divide_graph_into_parts(X_MIN, X_MAX, Y_MIN, Y_MAX, num_of_qubits_for_one_point, existing_charging_points, points_of_interest, powergrids, factor_power, save_grids=False, numbering=False):
    total_parts = 2 ** num_of_qubits_for_one_point

    if numbering:
        print(f"Graph #: {factor_power}")

    if num_of_qubits_for_one_point >= 3:
        factor1 = 2 ** factor_power
        factor2 = total_parts // factor1

        charging_x, charging_y = zip(*existing_charging_points)
        interest_x, interest_y = zip(*points_of_interest)
        power_x, power_y = zip(*powergrids)

        plt.scatter(charging_x, charging_y, color='red', alpha=0.7)
        plt.scatter(interest_x, interest_y, color='green', alpha=0.7)
        plt.scatter(power_x, power_y, color='orange', alpha=0.7)

        plt.xlim(X_MIN, X_MAX)
        plt.ylim(Y_MIN, Y_MAX)

        boundaries_dict = {}

        for i in range(factor1):
            for j in range(factor2):
                x_start = X_MIN + i * (X_MAX - X_MIN) / factor1
                x_end = X_MIN + (i + 1) * (X_MAX - X_MIN) / factor1
                y_start = Y_MIN + j * (Y_MAX - Y_MIN) / factor2
                y_end = Y_MIN + (j + 1) * (Y_MAX - Y_MIN) / factor2

                if save_grids:
                    grid_number = i * factor2 + j
                    adjacent_pairs = []

                    if i > 0:
                        adjacent_pairs.append((i - 1) * factor2 + j)
                    if i < factor1 - 1:
                        adjacent_pairs.append((i + 1) * factor2 + j)
                    if j > 0:
                        adjacent_pairs.append(i * factor2 + (j - 1))
                    if j < factor2 - 1:
                        adjacent_pairs.append(i * factor2 + (j + 1))
                    if i > 0 and j > 0:
                        adjacent_pairs.append((i - 1) * factor2 + (j - 1))
                    if i > 0 and j < factor2 - 1:
                        adjacent_pairs.append((i - 1) * factor2 + (j + 1))
                    if i < factor1 - 1 and j > 0:
                        adjacent_pairs.append((i + 1) * factor2 + (j - 1))
                    if i < factor1 - 1 and j < factor2 - 1:
                        adjacent_pairs.append((i + 1) * factor2 + (j + 1))

                    adjacent_pairs.sort()

                    boundaries_dict[grid_number] = {'x_start': x_start, 'x_end': x_end, 'y_start': y_start, 'y_end': y_end, 'adjacent_pairs': adjacent_pairs}

                plt.axhline(y=y_start, color='black', linestyle='--', linewidth=0.5)
                plt.axvline(x=x_start, color='black', linestyle='--', linewidth=0.5)
                plt.annotate(f'{i * factor2 + j}', ((x_start + x_end) / 2, (y_start + y_end) / 2), ha='center', va='center', fontsize=8, color='red')

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title(f'Divided Graph into {total_parts} Equal Parts using {factor1} x {factor2} grid')

        plt.show()

    else:
        factor1, factor2 = 1, total_parts

        plt.scatter(*zip(*all_coordinates), color='blue', alpha=0.7)

        plt.xlim(X_MIN, X_MAX)
        plt.ylim(Y_MIN, Y_MAX)

        boundaries_dict = {}

        for i in range(factor1):
            for j in range(factor2):
                x_start = X_MIN + i * (X_MAX - X_MIN) / factor1
                x_end = X_MIN + (i + 1) * (X_MAX - X_MIN) / factor1
                y_start = Y_MIN + j * (Y_MAX - Y_MIN) / factor2
                y_end = Y_MIN + (j + 1) * (Y_MAX - Y_MIN) / factor2

                if save_grids:
                    grid_number = i * factor2 + j
                    adjacent_pairs = []

                    if j > 0:
                        adjacent_pairs.append(i * factor2 + (j - 1))
                    if j < factor2 - 1:
                        adjacent_pairs.append(i * factor2 + (j + 1))

                    boundaries_dict[grid_number] = {'x_start': x_start, 'x_end': x_end, 'y_start': y_start, 'y_end': y_end, 'adjacent_pairs': adjacent_pairs}

                plt.axhline(y=y_start, color='black', linestyle='--', linewidth=0.5)
                plt.axvline(x=x_start, color='black', linestyle='--', linewidth=0.5)
                plt.annotate(f'{i * factor2 + j}', ((x_start + x_end) / 2, (y_start + y_end) / 2), ha='center', va='center', fontsize=8, color='red')

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title(f'Divided Graph into {total_parts} Equal Parts')

        plt.show()

    return boundaries_dict


def check_possibilities(X_MIN, X_MAX, Y_MIN, Y_MAX, num_of_qubits_for_one_point, existing_charging_points, points_of_interest, powergrids):
    for i in range(1, num_of_qubits_for_one_point):
        divide_graph_into_parts(X_MIN, X_MAX, Y_MIN, Y_MAX, num_of_qubits_for_one_point, existing_charging_points, points_of_interest, powergrids, i, numbering = True)


# This is to represent the boundaries dictionary
def display_boundaries_table(boundaries_dict, points_counts):
    if boundaries_dict is not None:
        table = PrettyTable()
        table.field_names = ["Grid Number", "X Start", "X End", "Y Start", "Y End", "Adjacent Pairs", "Existing Charging Points", "Points of Interest", "Power Grids"]

        for grid_number, boundary_info in boundaries_dict.items():
            charging_points = points_counts[grid_number]['charging_points']
            points_of_interest = points_counts[grid_number]['points_of_interest']
            powergrids = points_counts[grid_number]['powergrids']  # Assuming you have added 'power_grids' to the points_counts dictionary
            adjacent_pairs = ', '.join(map(str, boundary_info.get('adjacent_pairs', [])))

            table.add_row([grid_number, boundary_info['x_start'], boundary_info['x_end'], boundary_info['y_start'], boundary_info['y_end'], adjacent_pairs, charging_points, points_of_interest, powergrids])

        print(table)
    else:
        print("No grid boundaries to display.")



def count_points_in_grids(existing_charging_points, points_of_interest, powergrids, boundaries_dict):
    grid_counts = {}

    for grid_number, boundaries in boundaries_dict.items():
        x_start, x_end, y_start, y_end = boundaries['x_start'], boundaries['x_end'], boundaries['y_start'], boundaries['y_end']

        charging_in_grid = sum(x_start <= x <= x_end and y_start <= y <= y_end for x, y in existing_charging_points)
        interest_in_grid = sum(x_start <= x <= x_end and y_start <= y <= y_end for x, y in points_of_interest)
        power_in_grid = sum(x_start <= x <= x_end and y_start <= y <= y_end for x, y in powergrids)

        grid_counts[grid_number] = {'charging_points': charging_in_grid, 'points_of_interest': interest_in_grid, 'powergrids': power_in_grid}

    return grid_counts


def create_fitness_dict(boundaries_dict, points_counts):
    fitness_dict = {}

    for grid_number, boundary_info in boundaries_dict.items():
        charging_points = points_counts[grid_number]['charging_points']
        points_of_interest = points_counts[grid_number]['points_of_interest']
        powergrids = points_counts[grid_number]['powergrids']  # Assuming you have added 'power_grids' to the points_counts dictionary
        adjacent_pairs = []
        for _ in boundary_info.get('adjacent_pairs'):
            adjacent_pairs.append(_)

        fitness_dict[grid_number] = {'Adjacent_Pairs': adjacent_pairs, 'Charging Points': charging_points, 'Points of Interest': points_of_interest, 'Power Grids': powergrids}

    return fitness_dict


def display_fitness_table(fitness_dict):
    if fitness_dict:
        table = PrettyTable()
        table.field_names = ["Grid Number", "Adjacent Pairs", "Charging Points", "Points of Interest", "Power Grids"]

        for grid_number, fitness_info in fitness_dict.items():
            adjacent_pairs = ', '.join(map(str, fitness_info.get('Adjacent_Pairs', [])))
            charging_points = fitness_info['Charging Points']
            points_of_interest = fitness_info['Points of Interest']
            powergrids = fitness_info.get('Power Grids', 0)  # Assuming you have changed it to 'Power Grids' in the fitness dictionary

            table.add_row([grid_number, adjacent_pairs, charging_points, points_of_interest, powergrids])

        print(table)
    else:
        print("Summary dictionary is empty.")