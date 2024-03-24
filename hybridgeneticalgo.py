import random
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from qiskit.providers.jobstatus import JobStatus
from qiskit.primitives import BackendSampler
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.providers.options import Options

import time
import copy
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


def encode_numbers_in_circuits(numbers, qubits):
    circuits = []

    for num in numbers:
        circuit = QuantumCircuit(qubits, qubits)
        
        binary_num = bin(num)[2:].zfill(5)
        for bit_idx, bit in enumerate(binary_num):
            if bit == '1':
                circuit.x(bit_idx)

        circuits.append(circuit)

    return circuits


def decode_circuits(circuits):
    # simulator = "ibmq_qasm_simulator"
    service = QiskitRuntimeService()
    # backend = service.least_busy(operational=True, simulator=False, min_num_qubits=127)
    # backend = 'ibmq_qasm_simulator'
    backend = service.get_backend(name='ibmq_qasm_simulator')
    
    
    #sampler = Sampler(backend=backend)

    decoded_numbers = []

    for circuit in circuits:
        #transpiled_circuit = transpile(circuit, simulator)
        circuit.measure_all()
        # transpiled_circuit = transpile(circuit, backend)
        # job = execute(transpiled_circuit, simulator, shots=1)
        # sampler = Sampler(options=options, backend=simulator)
        # new_circuit = transpile(circuit, backend)
        # sampler = BackendSampler(backend)
        job = backend.run(circuit, shots=1)
        #job = backend.run(new_circuit)
        #job = sampler.run(circuit)

        # Keep track of the job status
        '''
        while job.status() not in [JobStatus.DONE, JobStatus.CANCELLED, JobStatus.ERROR]:
            print(f"Job status: {job.status()}")
            time.sleep(1)  # Wait for 5 seconds before checking again
        '''
        
        #print(job.error_message())
        
        # Check the final job status
        
        if job.status() == JobStatus.CANCELLED:
            print("Job was cancelled.")
            
        elif job.status() == JobStatus.DONE:
            print("Job completed successfully!")
            # Process the result
        else:  # JobStatus.ERROR
            try:
                result = job.result()
            except Exception as e:
                print(f"Job encountered an error: {e}")
            else:
                print("Job completed with errors:")
                print(result.get_counts(circuit))
        
        
        # print(job.status())
        print(job.result())
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
    for idx, circuit in enumerate(circuits):
        print(circuit)
        print()
        

def one_point_crossover(parent_1, parent_2):
    num_qubits = parent_1.num_qubits
    crossover_point = random.randint(1, num_qubits - 1)

    child_1 = QuantumCircuit(num_qubits)
    child_1.compose(parent_1, range(crossover_point), inplace=True)
    child_1.compose(parent_2, range(crossover_point, num_qubits), inplace=True)

    child_2 = QuantumCircuit(num_qubits)
    child_2.compose(parent_2, range(crossover_point), inplace=True)
    child_2.compose(parent_1, range(crossover_point, num_qubits), inplace=True)

    return child_1, child_2


# Crossover
def crossover(parent_1, parent_2):
    child_1 = parent_1[:3]
    child_1.extend((parent_2[3], parent_2[4]))

    child_2 = parent_2[:3]
    child_2.extend((parent_1[3], parent_1[4]))

    return child_1, child_2


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
        

def mutation(child):
    mutating_circuit = random.randint(0, 4)
    mutation_qubit = random.randint(0, 3)
    random_index = random.randint(1, 2)

    qc = copy.deepcopy(child[mutating_circuit])

    gate_dictionary = {
        1: qc.x,        # X gate       # CNOT gate
        2: qc.swap      # SWAP gate
    }
    gate_function = gate_dictionary.get(random_index)
    if random_index == 1:
        gate_function(mutation_qubit)
    else:
        gate_function(mutation_qubit, mutation_qubit+1)


    child[mutating_circuit] = qc

    return child
