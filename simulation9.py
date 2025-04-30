from numba import njit
import numpy as np

# Program state
clock = None

# Statistical Counters
delayPort = None
delayCrane = None

# System state
portStatus = None # 1: ocuppy, 0: free
craneStatus = None # 1: ocuppy, 0: free

# Events 
# Inicializacion
# LLegada puerto
# Salida puerto
# LLegada recarga
# Salida recarga

@njit
def initialize()-> None:
    # Inicializar el sistema
    clock = 0
    delayPort = 0
    delayCrane = 0
    portStatus = np.zeros(6, dtype=np.int32)
    craneStatus = np.zeros(5, dtype=np.int32)
    

@njit
def main()-> None:
    initialize()
    
@njit
def nextEventType()-> int:
    pass
    
@njit
def arrivalPort()-> None:
    pass

@njit
def departurePort()-> None:
    pass

@njit
def arrivalCrane()-> None:
    pass

@njit
def departureCrane()-> None:
    pass

@njit
def report()-> None:
    pass

if __name__ == "__main__":
    main()
    
    while (numDepartedPort < 100):
        eventType = nextEventType()
        if (eventType == 1):
            arrivalPort()
        elif (eventType == 2):
            departurePort()
        elif (eventType == 3):
            arrivalCrane()
        elif (eventType == 4):
            departureCrane()
            
    report()

    
    
