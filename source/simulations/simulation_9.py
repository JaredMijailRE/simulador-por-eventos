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
        sf.delayPort = None
        sf.delayCrane = None

        # System state
        sf.portStatus = None # 1: ocuppy, 0: free
        sf.craneStatus = None # 1: ocuppy, 0: free
        sf.numDeparted = 0

        # Events 
        # Inicializacion
        # LLegada puerto
        # Salida puerto
        # LLegada recarga
        # Salida recarga

    def initialize(sf)-> None:
        
        # Inicializar el sistema
        sf.clock = 0
        sf.delayPort = 0
        sf.delayCrane = 0
        sf.portStatus = np.zeros(6, dtype=np.int32)
        sf.craneStatus = np.zeros(5, dtype=np.int32)
        


    def main(sf)-> np.ndarray:
        "main function to execute one simulation and get the results"
        sf.initialize()
        
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
        

    def nextEventType(sf)-> int:
        "get the next event type"
        

    def arrivalPort(sf)-> None:
        "arrival of a port event"


    def departurePort(sf)-> None:
        "departure of a port event"


    def arrivalCrane(sf)-> None:
        "arrival of a crane event"


    def departureCrane(sf)-> None:
        "departure of a crane event"


    def report(sf)-> None:
        "give a report of the simulation"
    
    def multipleSimulation(sf, nSimulations: int)-> None:
        "run multiple simulations and get the results"
        
        results = np.zeros((nSimulations, 5), dtype=np.float64)
        for i in range(nSimulations):
            results[i] = sf.main()
        return results.mean(axis=0), results.std(axis=0)

def generateReport(sf, results: np.ndarray)-> None:
    "generate a report of results in a file"


if __name__ == "__main__":
    sim = Simulation_9()
    sim.main()
    


    
    
