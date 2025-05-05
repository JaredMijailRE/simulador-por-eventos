# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from numba import jit
import numpy as np

# (Se pueden programar las estructuras de ser necesario)
from collections import deque
import heapq as hq

'''
Eventos de la simulacion:
    1. Llegada de un cliente al area de servicio de la cafeteria.
    2. Salida de la espera del area de servicio de comida caliente (y llegada al area de consumo de la cafeteria).
    3. Salida de la espera del area de servicio de sandwich (y llegada al area de consumo de la cafeteria).
    4. Salida de un cliente del area de consumo de la cafeteria.
'''

### Parametros de la simulacion ###
attention_Times = np.array([60,30], dtype=np.int32)  # Tiempo para comida caliente y para sandwich (segundos)
capacity = 200  # Capacidad del area de consumo
num_Clients_Required = 1000  # Numero de clientes a procesar completamente
# (Y parametros de generacion de tiempos)

### Definicion de variables ###
# Reloj de la simulacion
clock = None

# Estado del sistema
employees_Status = None  # 0: libre, 1: ocupado
next_Associated_Info = None  # Indice de empleado asociado a un evento de salida (tipo 2 o 3)
                             # Tiempo de inicio de consumo (tipo 4)
next_Event_Type = None
num_Consuming = None  # Numero de clientes en el area de consumo
time_Arrival_Hot = deque()  # Cola de clientes en el area de servicio de comida caliente
time_Arrival_Sandwich = deque()  # Cola de clientes en el area de servicio de sandwich
time_Arrival_Consumption = deque()  # Cola de clientes para el area de consumo (indica tiempo), si esta llena
time_Arrival_Consumption_Source = deque()  # Cola de clientes en el area de consumo (indica area de origen)
                                           # 1: comida caliente, 2: sandwich
time_Last_Event = None

# Contadores estadisticos
areas_Employees_Status = None
area_Num_Consuming = None  # Sumatoria de clientes en el area de consumo
area_Num_Waiting_Consumption = None  # Sumatoria de clientes en cola para consumo
area_Num_Waiting_Hot = None  # Sumatoria de clientes en cola de servicio para comida caliente
area_Num_Waiting_Sandwich = None  # Sumatoria de clientes en cola de servicio para sandwich
num_Delayed_Consumption = None  # Numero de clientes atendidos para el area de consumo
num_Delayed_Hot = None  # Numero de clientes atendidos en el area de servicio de comida caliente
num_Delayed_Sandwich = None # Numero de clientes atendidos en el area de servicio de sandwich
num_Done_Clients = None  # Numero de clientes salidos en el area de consumo
total_Delay_Consuming = None  # Tiempo total de espera en el area de consumo
total_Delay_For_Consumption = None  # Tiempo total de espera para el area de consumo
total_Delay_Hot = None  # Tiempo total de espera en el area de servicio de comida caliente
total_Delay_Sandwich = None  # Tiempo total de espera en el area de servicio de sandwich

# Lista de eventos
events_List = []  # Elementos de la forma (tiempo del evento, tipo de evento, informacion adicional)


@jit(nopython=True)
def rand_Uniform(low, high) -> float:  # (Probablemente importada, no se bien si debe ser uniforme)
    return np.random.uniform(low, high)



def initialize() -> None:
    global clock
    global employees_Status
    global num_Consuming
    global time_Last_Event
    global areas_Employees_Status
    global area_Num_Consuming
    global area_Num_Waiting_Consumption
    global area_Num_Waiting_Hot
    global area_Num_Waiting_Sandwich
    global num_Delayed_Consumption
    global num_Delayed_Hot
    global num_Delayed_Sandwich
    global num_Done_Clients
    global total_Delay_Consuming
    global total_Delay_For_Consumption
    global total_Delay_Hot
    global total_Delay_Sandwich
    global events_List

    # Inicializacion de reloj
    clock = 0.0

    # Incicializaion de variables de estado
    employees_Status = np.zeros(7, dtype=np.uint8)
    num_Consuming = 0
    time_Last_Event = 0.0

    # Inicializacion de contadores estadisticos
    num_Delayed_Consumption = 0
    num_Delayed_Hot = 0
    num_Delayed_Sandwich = 0
    num_Done_Clients = 0
    total_Delay_Consuming = 0.0
    total_Delay_For_Consumption = 0.0
    total_Delay_Hot = 0.0
    total_Delay_Sandwich = 0.0
    areas_Employees_Status = np.zeros(7, dtype=np.float32)
    area_Num_Consuming = 0.0
    area_Num_Waiting_Consumption = 0.0
    area_Num_Waiting_Hot = 0.0
    area_Num_Waiting_Sandwich = 0.0

    # Inicializacion de la lista de eventos
    hq.heappush(events_List, (clock + rand_Uniform(5, 15), 1, None))  # Primer evento de llegada al area de servicio



def timing() -> None:
    global clock
    global next_Associated_Info
    global next_Event_Type
    
    # Obtencion del siguiente tipo y actualizacion del reloj
    if events_List:
        clock, next_Event_Type, next_Associated_Info = hq.heappop(events_List)
    else:
        print(f'Sin eventos en la lista, a los {clock} segundos.')
        exit(1)



def update_Time_Stats() -> None:
    global clock
    global time_Last_Event
    global employees_Status
    global num_Consuming
    global time_Arrival_Consumption
    global time_Arrival_Hot
    global time_Arrival_Sandwich
    global areas_Employees_Status
    global area_Num_Consuming
    global area_Num_Waiting_Consumption
    global area_Num_Waiting_Hot
    global area_Num_Waiting_Sandwich

    # Calculo del ancho de la ventana de tiempo y actualizacion del tiempo del ultimo evento
    time_Since_Last_Event = clock - time_Last_Event
    time_Last_Event = clock

    # Actualizacion de areas estadisticas
    areas_Employees_Status += employees_Status * time_Since_Last_Event
    area_Num_Consuming += num_Consuming * time_Since_Last_Event
    area_Num_Waiting_Consumption += len(time_Arrival_Consumption) * time_Since_Last_Event
    area_Num_Waiting_Hot += len(time_Arrival_Hot) * time_Since_Last_Event
    area_Num_Waiting_Sandwich += len(time_Arrival_Sandwich) * time_Since_Last_Event



def arrive_Service() -> None:
    global attention_Times
    global clock
    global employees_Status
    global time_Arrival_Hot
    global time_Arrival_Sandwich
    global num_Delayed_Hot
    global num_Delayed_Sandwich
    global events_List

    # Proxima llegada al area de servicio
    hq.heappush(events_List, (clock + rand_Uniform(5, 15), 1, None))

    # Decision de area de servicio
    if rand_Uniform(0,1) < 0.8:

        # Area de servicio de comida caliente
        for i in range(6):
            if employees_Status[i] == 0:
                
                # Asignacion de empleado (el tiempo de espera se incrementa en 0.0)
                num_Delayed_Hot += 1
                employees_Status[i] = 1

                # Programacion de salida de la atencion
                hq.heappush(events_List, (clock + attention_Times[0], 2, i))
                break
        else:
            # En espera (empleados ocupados)
            time_Arrival_Hot.append(clock)
    else:

        # Area de servico de sandwich
        if employees_Status[6] == 0:

            # Asignacion de empleado (el tiempo de espera se incrementa en 0.0)
                num_Delayed_Sandwich += 1
                employees_Status[6] = 1

                # Programacion de salida de la atencion
                hq.heappush(events_List, (clock + attention_Times[1], 3, 6))
        else:
            # En espera (empleado ocupado)
            time_Arrival_Sandwich.append(clock)



def departure_Service_Hot() -> None:
    global attention_Times
    global capacity
    global clock
    global employees_Status
    global next_Associated_Info
    global num_Consuming
    global time_Arrival_Hot
    global time_Arrival_Consumption
    global time_Arrival_Consumption_Source
    global num_Delayed_Consumption
    global num_Delayed_Hot
    global total_Delay_Hot
    global events_List
    
    # Llegada al area de consumo
    if num_Consuming < capacity:
        
        # Espacio disponible
        num_Delayed_Consumption += 1
        num_Consuming += 1

        # Programacion de salida del area de consumo (y del sistema)
        hq.heappush(events_List, (clock + rand_Uniform(20, 40), 4, clock))
    else:

        # En espera (area de consumo llena)
        time_Arrival_Consumption.append(clock)
        time_Arrival_Consumption_Source.append(1)

    # Verificacion de cola de servicio de comida caliente
    if time_Arrival_Hot:

        # Hay clientes en espera (actualizacion de tiempo total de espera)
        delay = clock - time_Arrival_Hot.popleft()
        total_Delay_Hot += delay
        num_Delayed_Hot += 1

        # Programacion de salida de la atencion
        hq.heappush(events_List, (clock + attention_Times[0], 2, next_Associated_Info))
    else:

        # Nadie en espera (se desocupa el empleado)
        employees_Status[next_Associated_Info] = 0



def departure_Service_Sandwich() -> None:
    global attention_Times
    global capacity
    global clock
    global employees_Status
    global next_Associated_Info
    global num_Consuming
    global time_Arrival_Sandwich
    global time_Arrival_Consumption
    global time_Arrival_Consumption_Source
    global num_Delayed_Consumption
    global num_Delayed_Sandwich
    global total_Delay_Sandwich
    global events_List
    
    # Llegada al area de consumo
    if num_Consuming < capacity:
        
        # Espacio disponible
        num_Delayed_Consumption += 1
        num_Consuming += 1

        # Programacion de salida del area de consumo (y del sistema)
        hq.heappush(events_List, (clock + rand_Uniform(10, 20), 4, clock))
    else:

        # En espera (area de consumo llena)
        time_Arrival_Consumption.append(clock)
        time_Arrival_Consumption_Source.append(2)

    # Verificacion de cola de servicio de comida caliente 
    if time_Arrival_Sandwich:

        # Hay clientes en espera (actualizacion de tiempo total de espera)
        delay = clock - time_Arrival_Sandwich.popleft()
        total_Delay_Sandwich += delay
        num_Delayed_Sandwich += 1

        # Programacion de salida de la atencion
        hq.heappush(events_List, (clock + attention_Times[1], 3, next_Associated_Info))
    else:

        # Nadie en espera (se desocupa el empleado)
        employees_Status[next_Associated_Info] = 0



def departure_Consumption() -> None:
    global clock
    global num_Consuming
    global time_Arrival_Consumption
    global time_Arrival_Consumption_Source
    global num_Delayed_Consumption
    global num_Done_Clients
    global total_Delay_Consuming
    global total_Delay_For_Consumption
    global events_List

    # Salida de un cliente del sistema
    num_Done_Clients += 1
    total_Delay_Consuming += clock - next_Associated_Info

    # Verificacion de cola del area de consumo
    if time_Arrival_Consumption:

        # Hay clientes en espera (actualizacion de tiempo total de espera)
        delay = clock - time_Arrival_Consumption.popleft()
        total_Delay_For_Consumption += delay
        num_Delayed_Consumption += 1

        # Programacion de salida del area de consumo (y del sistema)
        source = time_Arrival_Consumption_Source.popleft()
        if source == 1:
            hq.heappush(events_List, (clock + rand_Uniform(20, 40), 4, clock))
        elif source == 2:
            hq.heappush(events_List, (clock + rand_Uniform(10, 20), 4, clock))
    else:

        # Nadie en espera (se desocupa el espacio)
        num_Consuming -= 1



def report() -> None:
    global areas_Employees_Status
    global area_Num_Consuming
    global area_Num_Waiting_Consumption
    global area_Num_Waiting_Hot
    global area_Num_Waiting_Sandwich
    global num_Delayed_Consumption
    global num_Delayed_Hot
    global num_Delayed_Sandwich
    global num_Done_Clients
    global total_Delay_Consuming
    global total_Delay_For_Consumption
    global total_Delay_Hot
    global total_Delay_Sandwich
    
    # Calculo e impresion de estadisticas
    print('\n------------------------------ Simulation Statistics ------------------------------\n')
    print(f'\n  Average delay in the service area: {(total_Delay_Hot + total_Delay_Sandwich) / (num_Delayed_Hot + num_Delayed_Sandwich):.2f} seconds')
    print(f'    Average delay for the hot food service area: {total_Delay_Hot / num_Delayed_Hot:.2f} seconds')
    print(f'    Average delay for the sandwich service area: {total_Delay_Sandwich / num_Delayed_Sandwich:.2f} seconds')
    print(f'\n  Average delay for the consumption area: {total_Delay_For_Consumption / num_Delayed_Consumption:.2f} seconds')
    print(f'\n  Average time consuming: {total_Delay_Consuming / num_Done_Clients:.2f} seconds')
    print(f'\n  Average number in service queue: {(area_Num_Waiting_Hot + area_Num_Waiting_Sandwich) / clock:.2f} clients')
    print(f'    Average number in hot food service queue: {area_Num_Waiting_Hot / clock:.2f} clients')
    print(f'    Average number in sandwich service queue: {area_Num_Waiting_Sandwich / clock:.2f} clients')
    print(f'\n  Average number in consumption queue: {area_Num_Waiting_Consumption / clock:.2f} clients')
    print(f'\n  Average number in consumption area (consuming): {area_Num_Consuming / clock:.2f} clients')
    print(f'\n  Employees occupation: {np.sum(areas_Employees_Status) / (clock * 7): .2f} %')
    print(f'    Hot food service employees occupation: {np.sum(areas_Employees_Status[:-1]) / (clock *6): .2f} %')
    for i in range(6):
        print(f'      - Employee {i + 1} occupation: {areas_Employees_Status[i] / (clock): .2f} %')
    print(f'    Sandwich service employee occupation: {areas_Employees_Status[6] / (clock): .2f} %')
    print(f'\n  Consumption area utilization: {area_Num_Consuming / (clock * capacity):.2f} %')
    print(f'\nTime simulation ended: {clock:.2f} seconds | {clock / 60:.2f} minutes | {clock / 3600:.2f} hours')
    print(f'\nTotally served number: {num_Done_Clients} clients\n')



def main() -> None:
    global num_Clients_Required
    global next_Event_Type
    global num_Done_Clients

    # Inicializacion de la simulacion
    initialize()

    # Ciclo de la simulacion
    while num_Done_Clients < num_Clients_Required:

        # Lectura de eventos
        timing()

        # Actualizacion de contadores estadisticos
        update_Time_Stats()

        # Decision de rutinas de eventos
        if next_Event_Type == 1:
            arrive_Service()
        elif next_Event_Type == 2:
            departure_Service_Hot()
        elif next_Event_Type == 3:
            departure_Service_Sandwich()
        elif next_Event_Type == 4:
            departure_Consumption()
    
    # Reporte y fin del experimento
    report()



# Ejecución del programa
if __name__ == '__main__':
    main()
