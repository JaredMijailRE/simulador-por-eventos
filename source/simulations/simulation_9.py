import numpy as np
import random
from numba.experimental import jitclass 
import heapq as hq


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
        sf.are_ports_free = lambda: len(sf.portHeap) < numPorts
        sf.are_cranes_free = lambda: len(sf.craneExitHeap) < numCreanes
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
        

        # Statistical Counters
        sf.num_Delay_Port = []
        sf.num_Delay_Crane = []
        sf.num_Load_Time = []
        sf.num_Unload_Time = []
        sf.numDeparted = 0


        # System state
        sf.portHeap = []
        sf.portQueue = []
        sf.craneQueue = []

    def main(sf)-> np.ndarray:
        "main function to execute one simulation and get the results"
        sf.start_simulation()
        
        while (sf.numDeparted < 100):
            eventType = sf.next_event_type()
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
        
        # Check first two events (direct numbers)
        for i in range(2):
            if sf.eventList[i] is not None and sf.eventList[i] < min_time:
                min_time = sf.eventList[i]
                min_index = i
        
        # Check heap events (crane and port exits)
        for i in range(2, 4):
            if sf.eventList[i] and len(sf.eventList[i]) > 0:
                heap_min = sf.eventList[i][0]  # Peek at minimum in heap
                if heap_min < min_time:
                    min_time = heap_min
                    min_index = i
        
        if min_index == -1:
            return sf.INIT_SIMULATION  # Default to INIT_SIMULATION if no events found
            
        # Map index to event type constant
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

        if(sf.are_ports_free()):
            sf.num_Delay_Port.append(0)
            hq.heappush(sf.portHeap, sf.clock)
            if(sf.are_cranes_free()):
                sf.num_Delay_Crane.append(0)
                time_unloading = sf.unloading_time()
                sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(time_unloading))
                sf.num_Unload_Time.append(time_unloading)
            else:
                sf.craneQueue.append(sf.clock)
        else:
            sf.portQueue.append(sf.clock)
            
        sf.insert_event(sf.ARRIVAL_PORT, sf.timing(sf.arrival_time()))

        

    def departure_crane(sf)-> None:
        "departure of a crane event"
        
        sf.remove_event(sf.DEPARTURE_CRANE)
        
        if(sf.is_queue_crane_empty() and not sf.is_queue_port_empty()):
            # sacamos de la fila
            arrival_time = sf.craneQueue.pop()
            # tomamos metrica
            sf.num_Delay_Crane.append(sf.clock - arrival_time)
            # agendamos salida remplazo y ocupamos
            sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(sf.unloading_time()))
            
        if(sf.will_load()):
            # agendamos salida puerto
            sf.insert_event(sf.DEPARTURE_PORT, sf.timing(sf.loading_time()))
            # tomamos metrica
            sf.num_Load_Time.append(sf.loading_time())
        else:
            # agendamos salida puerto en instante
            sf.insert_event(sf.DEPARTURE_PORT, sf.timing(0))


    def departure_port(sf)-> None:
        "departure of a port event"
        
        sf.remove_event(sf.DEPARTURE_PORT) # quitmaos el evento
        hq.heappop(sf.portHeap) # desocupamos el puerto
        
        if(sf.are_ports_free() and not sf.is_queue_port_empty()):
            # sacamos de la fila espera
            arrival_time = sf.portQueue.pop()
            # tomamos metrica
            sf.num_Delay_Port.append(sf.clock - arrival_time)
            # vemos si hay gruas disponibles
            if(sf.are_cranes_free()):
                # metrica espera
                sf.num_Delay_Crane.append(0)
                # agendamos salida remplazo y ocupamos
                time_unloading = sf.unloading_time()
                sf.insert_event(sf.DEPARTURE_CRANE, sf.timing(time_unloading))
                # tomamos metrica
                sf.num_Unload_Time.append(time_unloading)
            else:
                # ponemos fila espera gruas
                sf.craneQueue.append(sf.clock)
                
        sf.numDeparted += 1
                
            

    def end_simulation(sf)-> np.ndarray:
        "end the simulation"
        
        return np.array([np.mean(sf.num_Delay_Port), np.mean(sf.num_Delay_Crane), np.mean(sf.num_Load_Time), np.mean(sf.num_Unload_Time), sf.numDeparted, sf.clock])
    

def multiple_simulation(nSimulations: int)-> np.ndarray:
    "run multiple simulations and get the results"
    
    results = np.zeros((nSimulations, 6), dtype=np.float64)
    for i in range(nSimulations):
        sf = Simulation_9()
        results[i] = sf.main()
    return results.mean(axis=0), results.std(axis=0)

def generate_report(sf, results: np.ndarray)-> None:
    "generate a report of results in a file"


if __name__ == "__main__":
    sim = Simulation_9()
    print(sim.main())
    


    
    
