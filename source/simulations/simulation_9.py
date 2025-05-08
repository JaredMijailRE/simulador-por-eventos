import numpy as np
import random
from numba.experimental import jitclass 
import heapq as hq

@jitclass
class Simulation_9:
    
    def __init__(sf)-> None:
        # Simulation parameters
        numCreanes = 5
        numPorts = 6
        sf.arrival_time = lambda: random.uniform(0.5, 1.5)
        sf.loading_time = lambda: random.uniform(0.5, 1.5)
        sf.unloading_time = lambda: random.uniform(4.5, 9.5)
        loading_probability = 0.1
        sf.will_load = lambda: random.random() < loading_probability
        sf.are_ports_free = lambda: len(sf.portQueue) < numPorts
        sf.are_cranes_free = lambda: len(sf.craneQueue) < numCreanes

        # Event types           
        sf.INIT_SIMULATION = 0
        sf.ARRIVAL_PORT = 1
        sf.DEPARTURE_CRANE = 2
        sf.DEPARTURE_PORT = 3

        # Program state
        sf.clock = 0.0
        sf.eventQueue = []
        

        # Statistical Counters
        sf.num_Delay_Port = []
        sf.num_Delay_Crane = []
        sf.num_Load_Time = []
        sf.num_Unload_Time = []


        # System state
        sf.portQueue = []
        sf.craneQueue = []
        sf.unloadHeap = []
        sf.loadHeap = []

    def main(sf)-> np.ndarray:
        "main function to execute one simulation and get the results"
        
        while (sf.numDeparted < 100):
            eventType = sf.nextEventType()
            if (eventType == sf.INIT_SIMULATION):
                sf.start_simulation()
            elif (eventType == sf.ARRIVAL_PORT):
                sf.arrivalPort()
            elif (eventType == sf.DEPARTURE_CRANE):
                sf.departure_crane()
            elif (eventType == sf.DEPARTURE_PORT):
                sf.departure_port()
            

        sf.end_simulation()
                
        return sf.report()
    
    def timing(sf, move: float)-> float:
        "update the current time of the simulation"

    def next_event_type(sf)-> int:
        "get the next event type"

    def start_simulation(sf)-> None:
        "start the simulation"

    def end_simulation(sf)-> None:
        "end the simulation"

    def arrival_port(sf)-> None:
        "arrival of a port event"

        hq.heappush(sf.eventQueue, (sf.clock + sf.arrival_time()), sf.ARRIVAL_PORT)

    
        if(sf.will_load()):
            hq.heappush(sf.eventQueue, (sf.clock + sf.unloading_time()), sf.ARRIVAL_CRANE)

        else:
            hq.heappush(sf.eventQueue, (sf.clock + sf.unloading_time()), sf.DEPARTURE_PORT)

    def departure_crane(sf)-> None:
        "departure of a crane event"

    def departure_port(sf)-> None:
        "departure of a port event"

    def report(sf)-> None:
        "give a report of the simulation"
    

def multiple_simulation(nSimulations: int)-> np.ndarray:
    "run multiple simulations and get the results"
    
    results = np.zeros((nSimulations, 5), dtype=np.float64)
    for i in range(nSimulations):
        sf = Simulation_9()
        results[i] = sf.main()
    return results.mean(axis=0), results.std(axis=0)

def generate_report(sf, results: np.ndarray)-> None:
    "generate a report of results in a file"


if __name__ == "__main__":
    sim = Simulation_9()
    sim.main()
    


    
    
