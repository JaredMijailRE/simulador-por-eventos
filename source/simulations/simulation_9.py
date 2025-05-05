import numpy as np
from numba.experimental import jitclass 

@jitclass
class Simulation_9:
    
    def __init__(sf)-> None:
        # Simulation parameters
        numCreanes = 5
        numPorts = 6
        
        ARRIVAL_PORT = 1
        DEPARTURE_PORT = 2
        ARRIVAL_CRANE = 3
        DEPARTURE_CRANE = 4
        
        # Constants
        sf.OCCUPIED = 1
        sf.FREE = 0


        # Program state
        sf.clock = None
        sf.eventList = []        
        
        sf.arrivalPortHeap = []
        sf.departurePortHeap = []
        sf.arrivalCraneHeap = []
        sf.departureCraneHeap = []

        

        # Statistical Counters
        sf.num_Delay_Port = 0
        sf.num_Delay_Crane = 0
        sf.total_Delay_Port = 0
        sf.total_Delay_Crane = 0
        
        

        # System state
        sf.portStatus = np.zeros(numPorts, dtype=np.int32) # 1: ocuppy, 0: free
        sf.craneStatus = np.zeros(numCreanes, dtype=np.int32) # 1: ocuppy, 0: free
        sf.numDeparted = 0

        # Events 
        # Inicializacion
        # LLegada puerto
        # Salida puerto
        # LLegada recarga
        # Salida recarga


    def main(sf)-> np.ndarray:
        "main function to execute one simulation and get the results"
        
        while (sf.numDeparted < 100):
            eventType = sf.nextEventType()
            if (eventType == 1):
                sf.arrivalPort()
            elif (eventType == 2):
                sf.departurePort()
            elif (eventType == 3):
                sf.arrivalCrane()
            elif (eventType == 4):
                sf.departureCrane()
                
        return sf.report()
        
    def timing(sf)-> None:
        "timing of the simulation"

    def update_time_stats(sf)-> None:
        "update the time statistics"

    def next_event_type(sf)-> int:
        "get the next event type"
        

    def arrival_port(sf)-> None:
        "arrival of a port event"


    def departure_port(sf)-> None:
        "departure of a port event"


    def arrival_crane(sf)-> None:
        "arrival of a crane event"


    def departure_crane(sf)-> None:
        "departure of a crane event"


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
    


    
    
