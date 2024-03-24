import random
import copy

def classical_population_generator(filtered_population_space, population_size, num_new_charging_points):
    generation = []
    for _ in range(population_size):
        pop = random.sample(filtered_population_space, num_new_charging_points)
        generation.append(pop)

    return generation

def classical_fitness_function(individual, fitness_dict):
    total_fitness = 0
    used_grids = set()
    used_adjacent_grids = set()

    for grid_number in individual:
        if grid_number in used_grids or grid_number in used_adjacent_grids:
            total_fitness -= 2

        charging_in_grid = fitness_dict[grid_number]['Charging Points']
        adjacent_pairs = fitness_dict[grid_number]['Adjacent_Pairs']
        charging_in_adjacent_grids = any(fitness_dict[int(adjacent_grid)]['Charging Points'] > 0 for adjacent_grid in adjacent_pairs)

        points_of_interest_in_grid = fitness_dict[grid_number]['Points of Interest'] > 0
        points_of_interest_in_adjacent_grids = any(fitness_dict[int(adjacent_grid)]['Points of Interest'] > 0 for adjacent_grid in adjacent_pairs)

        power_grids_in_grid = fitness_dict[grid_number]['Power Grids'] > 0
        power_grids_in_adjacent_grids = any(fitness_dict[int(adjacent_grid)]['Power Grids'] > 0 for adjacent_grid in adjacent_pairs)

        conditions_satisfied = sum([
            not charging_in_grid,
            not charging_in_adjacent_grids,
            points_of_interest_in_grid,
            points_of_interest_in_adjacent_grids,
            power_grids_in_grid,
            power_grids_in_adjacent_grids
        ])

        if conditions_satisfied == 6:
            grid_fitness = 6
        elif conditions_satisfied == 5:
            grid_fitness = 5
        elif conditions_satisfied == 4:
            grid_fitness = 4
        elif conditions_satisfied == 3:
            grid_fitness = 3
        elif conditions_satisfied == 2:
            grid_fitness = 2
        elif conditions_satisfied == 1:
            grid_fitness = 1
        else:
            grid_fitness = 0

        total_fitness += grid_fitness
        used_grids.add(grid_number)
        used_adjacent_grids.update(adjacent_pairs)

    return total_fitness

def classical_select_top_population(Generation, fitness_dict):
    fitness_scores = [(individual, classical_fitness_function(individual, fitness_dict)) for individual in Generation]

    sorted_population = sorted(fitness_scores, key=lambda x: x[1], reverse=True)

    top_population = [individual for individual, _ in sorted_population[:5]]

    return top_population

def classical_crossover(parent_1, parent_2):
    crossover_point = random.randint(1, len(parent_1) - 1)

    child_1 = parent_1[:crossover_point] + parent_2[crossover_point:]
    child_2 = parent_2[:crossover_point] + parent_1[crossover_point:]

    return child_1, child_2

def classical_generate_population(generation, lis_1, lis_2, num_of_qubits_for_one_point):
    combined_list = list(set(lis_1 + lis_2))

    while len(combined_list) < 5:
        new_number = random.randint(0, 2**num_of_qubits_for_one_point - 1)
        if new_number not in combined_list:
            combined_list.append(new_number)

    for _ in range(len(lis_1) - 1):
        child = random.sample(combined_list, 5)
        generation.append(child)




def classical_mutation(child, population_space, parent_1, parent_2):
    
    # Remove a random element from the child
    child.pop(random.randint(0, len(child) - 1))

    # Append an element from the population space that is not in either parent
    available_elements = set(population_space) - set(parent_1) - set(parent_2)
    new_element = random.choice(list(available_elements))
    child.append(new_element)

    return child




