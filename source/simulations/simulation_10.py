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


### Parametros del programa ###
reps = 150
reps_Shown = 5

### Parametros de la simulacion ###
attention_Times = np.array([60,30], dtype=np.int32)  # Tiempo para comida caliente y para sandwich (segundos)
capacity = 200  # Capacidad del area de consumo
num_Clients_Required = 1000  # Numero de clientes a procesar completamente
# (Y parametros de generacion de tiempos)


# Se opto por utilizar una clase para dar claridad y no invocar las variables globales en cada funcion
class Simulation_10:
    ''' Clase para la simulacion de la cafeteria '''
    
    def __init__(self, attention_Times, capacity, num_Clients_Required):
        ''' Constructor de clase para la simulacion de la cafeteria'''

        self.attention_Times = attention_Times
        self.capacity = capacity
        self.num_Clients_Required = num_Clients_Required

    
        ### Definicion de variables ###
        # Reloj de la simulacion
        self.clock = None

        # Estado del sistema
        self.IDLE = 0  # Empleado libre
        self.BUSY = 1  # Empleado ocupado
        self.ORIGIN_HOT = 1  # Area de origen comida caliente
        self.ORIGIN_SANDWICH = 2  # Area de origen sandwich
        self.employees_Status = None  # 0: libre, 1: ocupado
        self.original_Arrive_Time = None  # Tiempo de llegada inicial al sistema asociado a un cliente (para reportar tiempos total de estancia)
        self.next_Associated_Info = None  # Indice de empleado asociado a un evento de salida (tipo 2 o 3)
                                          # Tiempo de inicio de consumo (tipo 4)
        self.next_Event_Type = None
        self.num_Consuming = None  # Numero de clientes en el area de consumo
        self.time_Arrival_Hot = None  # Cola de clientes en el area de servicio de comida caliente (tiempo de llegada a la cola y el original)
        self.time_Arrival_Sandwich = None  # Cola de clientes en el area de servicio de sandwich (tiempo de llegada a la cola, y el original)
        self.time_Arrival_Consumption = None  # Cola de clientes para el area de consumo, si estuviera llena (tiempo de llegada a la cola, el original y el area de origen)
                                              # Para el area de origen, 1: comida caliente, 2: sandwich
        self.time_Last_Event = None

        # Contadores estadisticos
        self.areas_Employees_Status = None
        self.area_Num_Consuming = None  # Sumatoria de clientes en el area de consumo
        self.area_Num_Waiting_Consumption = None  # Sumatoria de clientes en cola para consumo
        self.area_Num_Waiting_Hot = None  # Sumatoria de clientes en cola de servicio para comida caliente
        self.area_Num_Waiting_Sandwich = None  # Sumatoria de clientes en cola de servicio para sandwich
        self.num_Delayed_Consumption = None  # Numero de clientes atendidos para el area de consumo
        self.num_Delayed_Hot = None  # Numero de clientes atendidos en el area de servicio de comida caliente
        self.num_Delayed_Sandwich = None # Numero de clientes atendidos en el area de servicio de sandwich
        self.num_Done_Clients = None  # Numero de clientes salidos en el area de consumo
        self.total_Delay_Consuming = None  # Tiempo total de espera en el area de consumo
        self.total_Delay_For_Consumption = None  # Tiempo total de espera para el area de consumo
        self.total_Delay_Hot = None  # Tiempo total de espera en el area de servicio de comida caliente
        self.total_Delay_Sandwich = None  # Tiempo total de espera en el area de servicio de sandwich
        self.total_Time_In = None  # Tiempo total de estancia de los clientes en el sistema
        # Contadores adicionales para reporte de todas las repeticiones
        self.reps_Avgs = None  # Lista de los distintos promedios (exceptudando ocupacion individual de empleados) calculados a partir de los contadores
        self.avg_Employee_Occupation = None  # Lista de promedios de ocupacion individuales de los empleados
        self.sum_Reps_Avgs = np.zeros(16, dtype=np.float64)  # Lista de sumatorias de promedios (exceptuando ocupación individual) de todas las repeticiones
        self.sum_Avg_Employee_Occupation = np.zeros(7, dtype=np.float64)  # Lista de sumatorias de promedios de ocupacion individuales de los empleados

        # Lista de eventos
        self.events_List = None  # Elementos de la forma (tiempo del evento, tipo de evento, llegada original, informacion adicional)


    
    def rand_Uniform(self, low, high) -> float:  # (Probablemente importada, no se bien si debe ser uniforme)
        return np.random.uniform(low, high)



    def initialize(self) -> None:
        ''' Inicializacion de variables de la simulacion '''

        # Inicializacion de reloj
        self.clock = 0.0

        # Incicializaion de variables de estado
        self.employees_Status = np.zeros(7, dtype=np.uint8)
        self.num_Consuming = 0
        self.time_Arrival_Hot = deque()  
        self.time_Arrival_Sandwich = deque()  
        self.time_Arrival_Consumption = deque()  
        self.time_Last_Event = 0.0

        # Inicializacion de contadores estadisticos
        self.num_Delayed_Consumption = 0
        self.num_Delayed_Hot = 0
        self.num_Delayed_Sandwich = 0
        self.num_Done_Clients = 0
        self.total_Delay_Consuming = 0.0
        self.total_Delay_For_Consumption = 0.0
        self.total_Delay_Hot = 0.0
        self.total_Delay_Sandwich = 0.0
        self.total_Time_In = 0.0
        self.areas_Employees_Status = np.zeros(7, dtype=np.float32)
        self.area_Num_Consuming = 0.0
        self.area_Num_Waiting_Consumption = 0.0
        self.area_Num_Waiting_Hot = 0.0
        self.area_Num_Waiting_Sandwich = 0.0

        # Inicializacion de la lista de eventos
        self.events_List = []
        arrive_Time = self.clock + self.rand_Uniform(5, 15)
        hq.heappush(self.events_List, (arrive_Time, 1, arrive_Time, None))  # Primer evento de llegada al area de servicio



    def timing(self) -> None:
        ''' Lectura de eventos y actualizacion del reloj '''
        
        # Obtencion del siguiente tipo y actualizacion del reloj
        if self.events_List:
            self.clock, self.next_Event_Type, self.original_Arrive_Time, self.next_Associated_Info = hq.heappop(self.events_List)
        else:
            print(f'Sin eventos en la lista, a los {self.clock} segundos.')
            exit(1)



    def update_Time_Stats(self) -> None:
        ''' Actualizacion de contadores estadisticos '''

        # Calculo del ancho de la ventana de tiempo y actualizacion del tiempo del ultimo evento
        self.time_Since_Last_Event = self.clock - self.time_Last_Event
        self.time_Last_Event = self.clock

        # Actualizacion de areas estadisticas
        self.areas_Employees_Status += self.employees_Status * self.time_Since_Last_Event
        self.area_Num_Consuming += self.num_Consuming * self.time_Since_Last_Event
        self.area_Num_Waiting_Consumption += len(self.time_Arrival_Consumption) * self.time_Since_Last_Event
        self.area_Num_Waiting_Hot += len(self.time_Arrival_Hot) * self.time_Since_Last_Event
        self.area_Num_Waiting_Sandwich += len(self.time_Arrival_Sandwich) * self.time_Since_Last_Event



    def arrive_Service(self) -> None:
        ''' Llegada de un cliente al area de servicio de la cafeteria '''

        # Proxima llegada al area de servicio
        arrive_Time = self.clock + self.rand_Uniform(5, 15)
        hq.heappush(self.events_List, (arrive_Time, 1, arrive_Time, None))

        # Decision de area de servicio
        if self.rand_Uniform(0,1) < 0.8:

            # Area de servicio de comida caliente
            for i in range(6):
                if self.employees_Status[i] == self.IDLE:
                    
                    # Asignacion de empleado (el tiempo de espera se incrementa en 0.0)
                    self.num_Delayed_Hot += 1
                    self.employees_Status[i] = self.BUSY

                    # Programacion de salida de la atencion
                    hq.heappush(self.events_List, (self.clock + self.attention_Times[0], 2, self.original_Arrive_Time, i))
                    break
            else:
                # En espera (empleados ocupados)
                self.time_Arrival_Hot.append([self.clock, self.original_Arrive_Time])
        else:

            # Area de servico de sandwich
            if self.employees_Status[6] == self.IDLE:

                # Asignacion de empleado (el tiempo de espera se incrementa en 0.0)
                    self.num_Delayed_Sandwich += 1
                    self.employees_Status[6] = self.BUSY

                    # Programacion de salida de la atencion
                    hq.heappush(self.events_List, (self.clock + self.attention_Times[1], 3, self.original_Arrive_Time, 6))
            else:
                # En espera (empleado ocupado)
                self.time_Arrival_Sandwich.append([self.clock, self.original_Arrive_Time])



    def departure_Service_Hot(self) -> None:
        ''' Salida de la espera del area de servicio de comida caliente y llegada al area de consumo '''
        
        # Llegada al area de consumo
        if self.num_Consuming < self.capacity:
            
            # Espacio disponible
            self.num_Delayed_Consumption += 1
            self.num_Consuming += 1

            # Programacion de salida del area de consumo (y del sistema)
            hq.heappush(self.events_List, (self.clock + self.rand_Uniform(20, 40), 4, self.original_Arrive_Time, self.clock))
        else:

            # En espera (area de consumo llena)
            self.time_Arrival_Consumption.append([self.clock, self.original_Arrive_Time, self.ORIGIN_HOT])

        # Verificacion de cola de servicio de comida caliente
        if self.time_Arrival_Hot:

            # Hay clientes en espera (actualizacion de tiempo total de espera)
            time, arrive_Time = self.time_Arrival_Hot.popleft()
            delay = self.clock - time
            self.total_Delay_Hot += delay
            self.num_Delayed_Hot += 1

            # Programacion de salida de la atencion
            hq.heappush(self.events_List, (self.clock + self.attention_Times[0], 2, arrive_Time, self.next_Associated_Info))
        else:

            # Nadie en espera (se desocupa el empleado)
            self.employees_Status[self.next_Associated_Info] = self.IDLE



    def departure_Service_Sandwich(self) -> None:
        ''' Salida de la espera del area de servicio de sandwich y llegada al area de consumo '''
        
        # Llegada al area de consumo
        if self.num_Consuming < self.capacity:
            
            # Espacio disponible
            self.num_Delayed_Consumption += 1
            self.num_Consuming += 1

            # Programacion de salida del area de consumo (y del sistema)
            hq.heappush(self.events_List, (self.clock + self.rand_Uniform(10, 20), 4, self.original_Arrive_Time, self.clock))
        else:

            # En espera (area de consumo llena)
            self.time_Arrival_Consumption.append([self.clock, self.original_Arrive_Time, self.ORIGIN_SANDWICH])

        # Verificacion de cola de servicio de comida caliente 
        if self.time_Arrival_Sandwich:

            # Hay clientes en espera (actualizacion de tiempo total de espera)
            time, arrive_Time = self.time_Arrival_Sandwich.popleft()
            delay = self.clock - time
            self.total_Delay_Sandwich += delay
            self.num_Delayed_Sandwich += 1

            # Programacion de salida de la atencion
            hq.heappush(self.events_List, (self.clock + self.attention_Times[1], 3, arrive_Time, self.next_Associated_Info))
        else:

            # Nadie en espera (se desocupa el empleado)
            self.employees_Status[self.next_Associated_Info] = self.IDLE



    def departure_Consumption(self) -> None:
        ''' Salida de un cliente del area de consumo '''

        # Salida de un cliente del sistema
        self.num_Done_Clients += 1
        self.total_Delay_Consuming += (self.clock - self.next_Associated_Info)
        self.total_Time_In += (self.clock - self.original_Arrive_Time)

        # Verificacion de cola del area de consumo
        if self.time_Arrival_Consumption:

            # Hay clientes en espera (actualizacion de tiempo total de espera)
            time, arrive_Time, source = self.time_Arrival_Consumption.popleft()
            delay = self.clock - time
            self.total_Delay_For_Consumption += delay
            self.num_Delayed_Consumption += 1

            # Programacion de salida del area de consumo (y del sistema)
            if source == 1:
                hq.heappush(self.events_List, (self.clock + self.rand_Uniform(20, 40), 4, arrive_Time, self.clock))
            elif source == 2:
                hq.heappush(self.events_List, (self.clock + self.rand_Uniform(10, 20), 4, arrive_Time, self.clock))
        else:

            # Nadie en espera (se desocupa el espacio)
            self.num_Consuming -= 1



    def report(self, show = True) -> None:
        ''' Reporte de resultados de la simulacion '''
        
        # Calculo y actualizacion de estadisticas (se guardan para el reporte final)
        self.reps_Avgs = np.zeros(16, dtype=np.float64)
        self.avg_Employee_Occupation = np.zeros(7, dtype=np.float64)
        self.reps_Avgs[0] = (self.total_Delay_Hot + self.total_Delay_Sandwich) / (self.num_Delayed_Hot + self.num_Delayed_Sandwich)
        self.reps_Avgs[1] = self.total_Delay_Hot / self.num_Delayed_Hot
        self.reps_Avgs[2] = self.total_Delay_Sandwich / self.num_Delayed_Sandwich
        self.reps_Avgs[3] = self.total_Delay_For_Consumption / self.num_Delayed_Consumption
        self.reps_Avgs[4] = self.total_Delay_Consuming / self.num_Done_Clients
        self.reps_Avgs[5] = self.total_Time_In / self.num_Done_Clients
        self.reps_Avgs[6] = (self.area_Num_Waiting_Hot + self.area_Num_Waiting_Sandwich) / self.clock
        self.reps_Avgs[7] = self.area_Num_Waiting_Hot / self.clock
        self.reps_Avgs[8] = self.area_Num_Waiting_Sandwich / self.clock
        self.reps_Avgs[9] = self.area_Num_Waiting_Consumption / self.clock
        self.reps_Avgs[10] = self.area_Num_Consuming / self.clock
        self.reps_Avgs[11] = np.sum(self.areas_Employees_Status) / (self.clock * 7)
        self.reps_Avgs[12] = np.sum(self.areas_Employees_Status[:-1]) / (self.clock *6)
        self.reps_Avgs[13] = self.area_Num_Consuming / (self.clock * capacity)
        self.reps_Avgs[14] = self.clock
        self.reps_Avgs[15] = self.num_Done_Clients
        self.avg_Employee_Occupation = self.areas_Employees_Status / self.clock
        self.sum_Reps_Avgs += self.reps_Avgs
        self.sum_Avg_Employee_Occupation += self.avg_Employee_Occupation
        
        # Impresion de resultados
        if show:
            print('\nStatistics\n')
            print(f'\n  Average delay in the service area: {self.reps_Avgs[0]:.2f} seconds')
            print(f'    Average delay for the hot food service area: {self.reps_Avgs[1]:.2f} seconds')
            print(f'    Average delay for the sandwich service area: {self.reps_Avgs[2]:.2f} seconds')
            print(f'\n  Average delay for the consumption area: {self.reps_Avgs[3]:.2f} seconds')
            print(f'\n  Average time consuming: {self.reps_Avgs[4]:.2f} seconds')
            print(f'\n  Average time in the system: {self.reps_Avgs[5]:.2f} seconds')
            print(f'\n  Average number in service queue: {self.reps_Avgs[6]:.2f} clients')
            print(f'    Average number in hot food service queue: {self.reps_Avgs[7]:.2f} clients')
            print(f'    Average number in sandwich service queue: {self.reps_Avgs[8]:.2f} clients')
            print(f'\n  Average number in consumption queue: {self.reps_Avgs[9]:.2f} clients')
            print(f'\n  Average number in consumption area (consuming): {self.reps_Avgs[10]:.2f} clients')
            print(f'\n  Employees occupation: {self.reps_Avgs[11] * 100:.2f} %')
            print(f'    Hot food service employees occupation: {self.reps_Avgs[12] * 100:.2f} %')
            for i in range(6):
                print(f'      - Employee {i + 1} occupation: {self.avg_Employee_Occupation[i] * 100:.2f} %')
            print(f'    Sandwich service employee occupation: {self.avg_Employee_Occupation[6] * 100:.2f} %')
            print(f'\n  Consumption area utilization: {self.reps_Avgs[13] * 100:.2f} %')
            print(f'\nTime simulation ended: {self.clock:.2f} seconds | {self.clock / 60:.2f} minutes | {self.clock / 3600:.2f} hours')
            print(f'\nTotally served number: {self.num_Done_Clients} clients\n')
    


    def final_Report(self, reps) -> None:
        ''' Reporte final de resultados de todos los experimentos'''

        # Impresion de resultados
        print(f'----------------------------------------------------------------------------')
        print(f'\n\n\n\n============================== Final Summary ===============================')
        print('\nParameters')
        print(f'\n  Capacity of the consumption area: {self.capacity} clients')
        print(f'\n  Service attention time for hot food area: {self.attention_Times[0]:.2f} seconds')
        print(f'\n  Service attention time for sandwich area: {self.attention_Times[1]:.2f} seconds')
        print(f'\n\nStatistics (Average of {reps} experiments)')
        print(f'\n  Average delay in the service area: {self.sum_Reps_Avgs[0] / reps:.2f} seconds')
        print(f'    Average delay for the hot food service area: {self.sum_Reps_Avgs[1] / reps:.2f} seconds')
        print(f'    Average delay for the sandwich service area: {self.sum_Reps_Avgs[2] / reps:.2f} seconds')
        print(f'\n  Average delay for the consumption area: {self.sum_Reps_Avgs[3] / reps:.2f} seconds')
        print(f'\n  Average time consuming: {self.sum_Reps_Avgs[4] / reps:.2f} seconds')
        print(f'\n  Average time in the system: {self.sum_Reps_Avgs[5] / reps:.2f} seconds')
        print(f'\n  Average number in service queue: {self.sum_Reps_Avgs[6] / reps:.2f} clients')
        print(f'    Average number in hot food service queue: {self.sum_Reps_Avgs[7] / reps:.2f} clients')
        print(f'    Average number in sandwich service queue: {self.sum_Reps_Avgs[8] / reps:.2f} clients')
        print(f'\n  Average number in consumption queue: {self.sum_Reps_Avgs[9] / reps:.2f} clients')
        print(f'\n  Average number in consumption area (consuming): {self.sum_Reps_Avgs[10] / reps:.2f} clients')
        print(f'\n  Employees occupation: {self.sum_Reps_Avgs[11] * 100 / reps: .2f} %')
        print(f'    Hot food service employees occupation: {self.sum_Reps_Avgs[12] * 100 / reps:.2f} %')
        for i in range(6):
            print(f'      - Employee {i + 1} occupation: {self.sum_Avg_Employee_Occupation[i] * 100 / reps:.2f} %')
        print(f'    Sandwich service employee occupation: {self.sum_Avg_Employee_Occupation[6] * 100 / reps:.2f} %')
        print(f'\n  Consumption area utilization: {self.sum_Reps_Avgs[13] * 100 / reps:.2f} %')
        print(f'\nTime simulation ended: {self.sum_Reps_Avgs[14] / reps:.2f} seconds | {self.sum_Reps_Avgs[14] / (reps * 60):.2f} minutes | {self.sum_Reps_Avgs[14] / (reps * 3600):.2f} hours')
        print(f'\nTotally served number: {self.sum_Reps_Avgs[15] / reps} clients\n')



    def main(self, reps, reps_Shown) -> None:
        ''' Funcion principal de la simulacion (modificada para repeticion de experimentos)'''

        if reps > 1:
            print(f'\n\nReports of the first experiments are shown ({reps_Shown} of {reps}):\n')

        # Repeticiones de la simulacion (experimentos)
        for i in range(reps):

            # Inicializacion de la simulacion
            self.initialize()

            # Ciclo de la simulacion
            while self.num_Done_Clients < self.num_Clients_Required:

                # Lectura de eventos
                self.timing()

                # Actualizacion de contadores estadisticos
                self.update_Time_Stats()

                # Decision de rutinas de eventos
                if self.next_Event_Type == 1:
                    self.arrive_Service()
                elif self.next_Event_Type == 2:
                    self.departure_Service_Hot()
                elif self.next_Event_Type == 3:
                    self.departure_Service_Sandwich()
                elif self.next_Event_Type == 4:
                    self.departure_Consumption()

            if i < reps_Shown:
                print(f'\n\n\n------------------------------ Simulation {i + 1} ------------------------------')

                # Reporte y fin del experimento
                self.report()
            else:
                self.report(show = False)
        
        if reps > 1:
            self.final_Report(reps)



# Ejecución del programa
if __name__ == '__main__':
    simulation = Simulation_10(attention_Times, capacity, num_Clients_Required)
    simulation.main(reps, reps_Shown)
