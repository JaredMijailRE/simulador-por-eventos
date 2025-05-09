import numpy as np
import random
import heapq as hq

class Simulation_9:
    
    def __init__(sf)-> None:
        # Simulation parameters
        sf.numCranes = 5
        sf.numPorts = 6
        sf.arrival_time = lambda: random.uniform(0.5, 1.5)
        sf.loading_time = lambda: random.uniform(0.5, 1.5)
        sf.unloading_time = lambda: random.uniform(4.5, 10.5)
        loading_probability = 0.1
        sf.will_load = lambda: random.random() < loading_probability
        sf.are_ports_free = lambda: len(sf.portHeap) < sf.numPorts
        sf.are_cranes_free = lambda: len(sf.craneExitHeap) < sf.numCranes
        sf.is_queue_port_empty = lambda: len(sf.portQueue) == 0
        sf.is_queue_crane_empty = lambda: len(sf.craneQueue) == 0

        # Event types           
        sf.INIT_SIMULATION = 0
        sf.ARRIVAL_PORT = 1
        sf.DEPARTURE_CRANE = 2
        sf.DEPARTURE_PORT = 3

        # Program state
        sf.clock = 0.0
        sf.craneExitHeap = []
        sf.portExitHeap = []
        sf.eventList = [None, None, sf.craneExitHeap, sf.portExitHeap]
        
        # Statistical Counters (for individual observations)
        sf.stat_Port_Delays = []
        sf.stat_Crane_Delays = []
        sf.stat_Load_Times = []
        sf.stat_Unload_Times = []
        sf.stat_Arrival_Times = []
        sf.stat_Port_Occupancy_Durations = []
        sf.numDeparted = 0

        # Time-Averaged Statistical Accumulators
        sf.time_last_event = 0.0
        sf.area_num_in_port_queue = 0.0
        sf.area_num_in_crane_queue = 0.0
        sf.area_busy_ports = 0.0
        sf.area_busy_cranes = 0.0

        # System state
        sf.portHeap = []
        sf.portQueue = []
        sf.craneQueue = []

    def record_stat(sf, list_attribute_name: str, value: float) -> None:
        """Helper function to append a value to a specified statistics list."""
        getattr(sf, list_attribute_name).append(value)

    def update_time_avg_stats(sf) -> None:
        """Update time-averaged statistical accumulators."""
        time_since_last_event = sf.clock - sf.time_last_event
        sf.time_last_event = sf.clock

        sf.area_num_in_port_queue += len(sf.portQueue) * time_since_last_event
        sf.area_num_in_crane_queue += len(sf.craneQueue) * time_since_last_event
        sf.area_busy_ports += len(sf.portHeap) * time_since_last_event
        sf.area_busy_cranes += len(sf.craneExitHeap) * time_since_last_event

    def main(sf)-> np.ndarray:
        "main function to execute one simulation and get the results"
        sf.start_simulation()
        
        while (sf.numDeparted < 100):
            eventType = sf.next_event_type()
            sf.update_time_avg_stats() 

            if (eventType == sf.ARRIVAL_PORT):
                sf.arrival_port()
            elif (eventType == sf.DEPARTURE_CRANE):
                sf.departure_crane()
            elif (eventType == sf.DEPARTURE_PORT):
                sf.departure_port()
            
        return sf.end_simulation()
    
    def timing(sf, move: float)-> float:
        "update the current time of the simulation"
        return sf.clock + move

    def next_event_type(sf)-> int:
        "get the next event type"
        min_time = float('inf')
        min_index = -1
        
        for i in range(2):
            if sf.eventList[i] is not None and sf.eventList[i] < min_time:
                min_time = sf.eventList[i]
                min_index = i
        
        for i in range(2, 4):
            if sf.eventList[i] and len(sf.eventList[i]) > 0:
                heap_min = sf.eventList[i][0] 
                if heap_min < min_time:
                    min_time = heap_min
                    min_index = i
        
        if min_index == -1:
            return sf.INIT_SIMULATION  
            
        event_types = [sf.INIT_SIMULATION, sf.ARRIVAL_PORT, sf.DEPARTURE_CRANE, sf.DEPARTURE_PORT]
        
        sf.clock = min_time
        return event_types[min_index]

    def insert_event(sf, event: int, time: float)-> None:
        "insert an event in the event list"
        if(event == 0 or event == 1):
            sf.eventList[event] = time
        else:
            hq.heappush(sf.eventList[event], time)
    
    def remove_event(sf, event: int)-> None:
        "remove an event from the event list"
        if(event == 0):
            sf.eventList[event] = None
        else:
            hq.heappop(sf.eventList[event])

    def start_simulation(sf)-> None:
        "start the simulation"
        sf.insert_event(sf.ARRIVAL_PORT, sf.clock)

    def arrival_port(sf)-> None:
        "arrival of a port event"
        current_arrival_time = sf.arrival_time()
        sf.record_stat("stat_Arrival_Times", current_arrival_time)

        if(sf.are_ports_free()):
            sf.record_stat("stat_Port_Delays", 0)
            hq.heappush(sf.portHeap, sf.clock)
            if(sf.are_cranes_free()):
                sf.record_stat("stat_Crane_Delays", 0)
                time_unloading = sf.unloading_time()
                sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(time_unloading))
                sf.record_stat("stat_Unload_Times", time_unloading)
            else:
                sf.craneQueue.append(sf.clock)
        else:
            sf.portQueue.append(sf.clock)
            
        sf.insert_event(sf.ARRIVAL_PORT, sf.timing(current_arrival_time))

        

    def departure_crane(sf)-> None:
        "departure of a crane event"
        
        sf.remove_event(sf.DEPARTURE_CRANE)
        
        if sf.will_load():
            time_loading = sf.loading_time()
            sf.record_stat("stat_Load_Times", time_loading)
            sf.insert_event(sf.DEPARTURE_PORT, sf.timing(time_loading))
        else:
            sf.insert_event(sf.DEPARTURE_PORT, sf.timing(0))

        if not sf.is_queue_crane_empty():
            arrival_time_in_crane_queue = sf.craneQueue.pop(0)
            sf.record_stat("stat_Crane_Delays", sf.clock - arrival_time_in_crane_queue)
            
            time_unloading = sf.unloading_time()
            sf.record_stat("stat_Unload_Times", time_unloading)
            sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(time_unloading))


    def departure_port(sf)-> None:
        "departure of a port event"
        
        sf.remove_event(sf.DEPARTURE_PORT)
        port_occupation_start_time = hq.heappop(sf.portHeap)
        sf.record_stat("stat_Port_Occupancy_Durations", sf.clock - port_occupation_start_time)
        
        if not sf.is_queue_port_empty():
            arrival_time = sf.portQueue.pop(0)
            sf.record_stat("stat_Port_Delays", sf.clock - arrival_time)
            
            hq.heappush(sf.portHeap, sf.clock)
            
            if(sf.are_cranes_free()):
                sf.record_stat("stat_Crane_Delays", 0)
                time_unloading = sf.unloading_time()
                sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(time_unloading))
                sf.record_stat("stat_Unload_Times", time_unloading)
                
        sf.numDeparted += 1
                
            

    def end_simulation(sf)-> np.ndarray:
        "end the simulation"
        
        if sf.clock > sf.time_last_event: 
             sf.update_time_avg_stats() 

        avg_num_in_port_queue = (sf.area_num_in_port_queue / sf.clock) if sf.clock > 0 else 0
        avg_num_in_crane_queue = (sf.area_num_in_crane_queue / sf.clock) if sf.clock > 0 else 0
        
        port_utilization = (sf.area_busy_ports / (sf.numPorts * sf.clock)) if sf.clock > 0 and sf.numPorts > 0 else 0
        crane_utilization = (sf.area_busy_cranes / (sf.numCranes * sf.clock)) if sf.clock > 0 and sf.numCranes > 0 else 0

        return np.array([
            np.mean(sf.stat_Port_Delays) if sf.stat_Port_Delays else 0,
            np.mean(sf.stat_Crane_Delays) if sf.stat_Crane_Delays else 0,
            np.mean(sf.stat_Load_Times) if sf.stat_Load_Times else 0,
            np.mean(sf.stat_Unload_Times) if sf.stat_Unload_Times else 0,
            sf.numDeparted, 
            sf.clock,
            np.mean(sf.stat_Arrival_Times) if sf.stat_Arrival_Times else 0,
            avg_num_in_port_queue,  
            avg_num_in_crane_queue, 
            port_utilization,      
            crane_utilization       
        ])
    

def multiple_simulation(nSimulations: int)-> np.ndarray:
    "run multiple simulations and get the results"
    
    results = np.zeros((nSimulations, 11), dtype=np.float64) 
    for i in range(nSimulations):
        sf = Simulation_9()
        results[i] = sf.main()
    return results.mean(axis=0), results.std(axis=0)

import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

def run_simulation_batch(n: int) -> np.ndarray:
    results = np.zeros((n, 11), dtype=np.float64) 
    for i in range(n):
        sf = Simulation_9()
        results[i] = sf.main()
    return results

def multiple_simulation_parallel(nSimulations: int) -> tuple[np.ndarray, np.ndarray]:
    n_cpus = multiprocessing.cpu_count()
    batch_sizes = [nSimulations // n_cpus] * n_cpus
    for i in range(nSimulations % n_cpus):
        batch_sizes[i] += 1

    with ProcessPoolExecutor(max_workers=n_cpus) as executor:
        futures = [executor.submit(run_simulation_batch, batch_size) for batch_size in batch_sizes]
        results = np.vstack([f.result() for f in futures])

    return results.mean(axis=0), results.std(axis=0)


def generate_report(sf, results: np.ndarray)-> None:
    "generate a report of results in a file"
    with open('simulation_9_report.txt', 'w') as f:
        f.write("Simulation 9 - Port and Crane Statistics Report\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Mean Values (across simulations):\n")
        f.write("-" * 30 + "\n")
        f.write(f"Port Delay (ships): {results[0]:.4f} hours\n")
        f.write(f"Crane Delay (ships): {results[1]:.4f} hours\n")
        f.write(f"Load Time (ships): {results[2]:.4f} hours\n")
        f.write(f"Unload Time (ships): {results[3]:.4f} hours\n")
        f.write(f"Departed Ships (total per sim): {results[4]:.0f}\n")
        f.write(f"Average Simulation Clock: {results[5]:.4f} hours\n")
        f.write(f"Average Inter-Arrival Time (ships): {results[6]:.4f} hours\n")
        f.write(f"Time-Avg Ships in Port Queue: {results[7]:.4f}\n") # New
        f.write(f"Time-Avg Ships in Crane Queue: {results[8]:.4f}\n") 
        f.write(f"Port Utilization: {results[9]*100:.2f}%\n")
        f.write(f"Crane Utilization: {results[10]*100:.2f}%\n\n")
        
        f.write("Simulation Parameters (per single run):\n")
        f.write("-" * 30 + "\n")
        f.write(f"Number of Cranes: 5\n") 
        f.write(f"Number of Ports: 6\n")
        f.write("Arrival Time: Uniform(0.5, 1.5) hours\n")
        f.write("Loading Time: Uniform(0.5, 1.5) hours\n")
        f.write("Unloading Time: Uniform(4.5, 10.5) hours\n")
        f.write("Loading Probability: 10%\n")
        f.write("Target Ships per Simulation: 100\n")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import time

    num_simulations = 10000 
    time_start = time.time()
    mean_results, std_results = multiple_simulation_parallel(num_simulations)
    time_end = time.time()
    print(f"Parallel simulation time for {num_simulations} runs: {time_end - time_start:.2f} seconds")
    
    generate_report(None, mean_results)
    plt.figure(figsize=(14, 8)) 
    x_labels = ["Port Delay", "Crane Delay", "Load Time", "Unload Time", 
                "Departed Ships", "Avg Sim Clock", "Avg Arrival Time", 
                "Avg in Port Q", "Avg in Crane Q", 
                "Port Util (%)", "Crane Util (%)"]
    
    plot_means = mean_results.copy()
    plot_std = std_results.copy()
    if len(plot_means) > 10:
        plot_means[9] *= 100 
        plot_means[10] *= 100
        plot_std[9] *= 100
        plot_std[10] *= 100

    plt.bar(x_labels, plot_means, yerr=plot_std, color='skyblue', label='Mean with Std Dev', capsize=5)
    plt.xlabel("Metrics")
    plt.ylabel("Values")
    plt.title(f"Simulation 9 Results (Means over {num_simulations} runs)")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()



    

    


    
    
