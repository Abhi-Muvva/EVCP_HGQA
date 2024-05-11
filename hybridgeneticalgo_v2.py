import copy
from qiskit import Aer, execute, transpile
from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_bloch_multivector, plot_histogram
import random


def population_generator(filtered_population_space, population_size, num_new_charging_points):
    generation = []
    for population in range(population_size):
        pop = random.sample(filtered_population_space, num_new_charging_points)
        generation.append(pop)

    return generation


def fitness_function(individual, fitness_dict):
    total_fitness = 0
    used_grids = set()
    used_adjacent_grids = set()

    for grid_number in individual:
        if grid_number in used_grids or grid_number in used_adjacent_grids:
            total_fitness -= 2  # Penalize if two new charging stations are in the same grid or in the adjacent grids

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



def select_top_population(Generation, fitness_dict):

    fitness_scores = [(individual, fitness_function(individual, fitness_dict)) for individual in Generation]

    sorted_population = sorted(fitness_scores, key=lambda x: x[1], reverse=True)

    top_population = [individual for individual, _ in sorted_population[:5]]
    '''
    for ind, fit in zip(top_population, fitness_scores):
        print(f"Individual: {ind}, Fitness Score: {fit}")
    '''

    return top_population


# def encode_numbers_in_circuit(numbers):
#     circuit = QuantumCircuit(5 * len(numbers), len(numbers))

#     for idx, num in enumerate(numbers):
#         binary_num = bin(num)[2:].zfill(5)
#         for bit_idx, bit in enumerate(binary_num):
#             if bit == '1':
#                 circuit.x(5 * idx + bit_idx)

#     return circuit


def encode_numbers_in_circuits(numbers):
    circuits = []

    for num in numbers:
        circuit = QuantumCircuit(5, 5)
        
        binary_num = bin(num)[2:].zfill(5)
        for bit_idx, bit in enumerate(binary_num):
            if bit == '1':
                circuit.x(bit_idx)

        circuits.append(circuit)

    return circuits


def decode_circuits(circuits):
    simulator = Aer.get_backend('qasm_simulator')

    decoded_numbers = []

    for circuit in circuits:
        transpiled_circuit = transpile(circuit, simulator)

        transpiled_circuit.measure_all()
        job = execute(transpiled_circuit, simulator, shots=1)
        result = job.result()

        counts = result.get_counts()

        if len(counts) == 0:
            print("No counts found. Check the circuit or simulation setup.")
            decoded_numbers.append(None)
            continue

        binary_result = list(counts.keys())[0]

        cleaned_binary_result = binary_result.replace(" ", "")
        reversed_binary_result = cleaned_binary_result[::-1]
        decimal_result = int(reversed_binary_result, 2)

        decoded_numbers.append(decimal_result)

    return decoded_numbers


def visualise_circuit(circuits):
    for idx, circuit in enumerate(encoded_circuits):
        print(circuit)
        print()


# Crossover
def crossover(parent_1, parent_2):
    child_1 = parent_1[:3]
    child_1.extend((parent_2[3], parent_2[4]))

    child_2 = parent_2[:3]
    child_2.extend((parent_1[3], parent_1[4]))

    return child_1, child_2


def mutation(child):
    mutating_circuit = random.randint(0, 4)
    mutation_qubit = random.randint(0, 3)
    random_index = random.randint(1, 3)

    qc = copy.deepcopy(child[mutating_circuit])

    gate_dictionary = {
        1: qc.x,        # X gate
        2: qc.cx,       # CNOT gate
        3: qc.swap      # SWAP gate
    }
    gate_function = gate_dictionary.get(random_index)
    if random_index == 1:
        gate_function(mutation_qubit)
    else:
        gate_function(mutation_qubit, mutation_qubit+1)


    child[mutating_circuit] = qc

    return child


def generate_population(generation, lis_1, lis_2, num_of_qubits_for_one_point):
    # Remove duplicates by converting lists to sets
    set1 = set(lis_1)
    set2 = set(lis_2)

    # Find the common elements and remove them from both sets
    common_elements = set1.intersection(set2)

    for common_element in common_elements:
        set2.remove(common_element)
    # Convert sets back to lists
    lis_1 = list(set1)
    lis_2 = list(set2)

    combined_list = lis_1 + lis_2

    while len(combined_list) < 5:
        new_number = random.randint(0, 2**num_of_qubits_for_one_point - 1)
        if new_number not in combined_list:
            combined_list.append(new_number)

    for i in range(len(lis_1) - 1):
        # Update lis_2 inside the loop to reflect its changing size
        lis_2_updated = lis_2.copy()
        
        # Generate a child list with 5 random elements from lis_1 and lis_2
        child = random.sample(combined_list, 5)
        generation.append(child)