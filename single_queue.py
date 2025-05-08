import numpy as np

class SimuladorAlmacen:
    def __init__(self, params):
        self.QLIMIT = params['num_delays_required']
        self.BUSY = 1
        self.IDLE = 0
        self.OPEN = 1
        self.CLOSED = 0
        self.SERVICE_A = 1
        self.SERVICE_B = 2
        self.NO_SERVICE = 3
        self.next_event_type = 0
        self.num_custs_delayed = 0
        self.num_delays_required = params['num_delays_required']
        self.num_events = 0
        self.num_in_q = 0
        self.server_status = 0
        self.store_status = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.area_total_income = 0.0
        self.mean_interarrival = params['mean_interarrival']
        self.mean_service_A_sup = params['mean_service_A_sup']
        self.mean_service_A_inf = params['mean_service_A_inf']
        self.mean_service_B = params['mean_service_B']
        self.mean_no_service = params['mean_no_service_']
        self.prob_service_A = params['prob_service_A']
        self.prob_service_B = params['prob_service_B']
        self.sales_A = params['sales_A']
        self.sales_B = params['sales_B']
        self.sales_no_service = params['sales_no_service']
        self.service_type = 0
        self.num_service_types = 3
        self.prob_no_service_ = 1 - (self.prob_service_A + self.prob_service_B)
        self.time_limit = params['time_limit']
        self.sim_time = 0.0
        self.time_arrival = np.zeros(self.QLIMIT + 1)
        self.time_last_event = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)  
        self.total_of_delays = 0.0
        self.service_counts = np.zeros(self.num_service_types + 1)  # Índices 1-3
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
    

    @staticmethod
    def exponential(beta):
        """Genera un número aleatorio con distribución exponencial."""
        u = np.random.rand()
        return -beta * np.log(u)

    def select_service(self):
        """Selecciona el tiempo de servicio basado en la probabilidad."""
        u = np.random.rand()
        service_type = 0
        if u < self.prob_service_A:
            service_type = self.SERVICE_A
        elif u < self.prob_service_A + self.prob_service_B:
            service_type = self.SERVICE_B
        else:
            service_type = self.NO_SERVICE
        return service_type
    
    def service_time(self, service_type):
        """Calcula el tiempo de servicio basado en el tipo de servicio."""
        if service_type == self.SERVICE_A:
            v = np.random.rand()
            range_A = self.mean_service_A_sup - self.mean_service_A_inf
            return v * range_A + self.mean_service_A_inf
        elif service_type == self.SERVICE_B:
            return self.exponential(self.mean_service_B)
        elif service_type == self.NO_SERVICE:
            return self.mean_no_service
        else:
            print("Error: Invalid service type", service_type)
            return 0.0
        
    def sales(self, service_type):
        if service_type == self.SERVICE_A:
            return self.sales_A
        elif service_type == self.SERVICE_B:
            return self.sales_B
        elif service_type == self.NO_SERVICE:
            return self.sales_no_service
        else:
            print("Error: Invalid service type", service_type)
            return 0.0
        
    def initialize(self):
        self.sim_time = 0.0
        self.server_status = self.IDLE
        self.store_status = self.OPEN
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.area_total_income = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)  
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        self.time_next_event[2] = float('inf')
        self.service_counts = np.zeros(self.num_service_types + 1)
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
        
    def timing(self):
        min_time_next_event = float('inf')
        self.next_event_type = 0
        for i in range(1, self.num_events + 1):
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i
        if self.next_event_type == 0:
            print("Event list is empty at time", self.sim_time)
            return
        if min_time_next_event > self.time_limit:
            self.store_status = self.CLOSED
        self.sim_time = min_time_next_event

    def arrive(self):
        if self.store_status == self.OPEN:
            self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        else:
            self.time_next_event[1] = float('inf')
        
        self.service_type = self.select_service()  # Actualiza la variable de instancia
        
        if self.server_status == self.BUSY:
            self.num_in_q += 1
            if self.num_in_q > self.QLIMIT:
                print("Overflow of the queue at time", self.sim_time)
            else:
                self.time_arrival[self.num_in_q] = self.sim_time
                self.service_type_arrival[self.num_in_q] = self.service_type  # Guarda el tipo de servicio
        else:
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status = self.BUSY
            service_time = self.service_time(self.service_type)
            self.time_next_event[2] = self.sim_time + service_time
            self.service_counts[self.service_type] += 1
            self.service_times[self.service_type] += service_time
        
    def depart(self):
    if self.num_in_q == 0:
        self.server_status = self.IDLE
        self.time_next_event[2] = float('inf')
    else:
        self.num_in_q -= 1
        service_type = int(self.service_type_arrival[1])
        delay = self.sim_time - self.time_arrival[1]
        self.total_of_delays += delay
        self.num_custs_delayed += 1
        
        service_time = self.service_time(service_type)
        if self.store_status == self.OPEN:
            self.time_next_event[2] = self.sim_time + service_time
        
        # Actualizar estadísticas
        self.service_counts[service_type] += 1
        self.service_times[service_type] += service_time
        self.queue_times[service_type] += delay
        
        # Calcular ventas solo cuando se atiende al cliente
        sale_amount = self.sales(service_type)
        self.sales_by_service[service_type] += sale_amount
        self.area_total_income += sale_amount
        
        # Reorganizar la cola
        for i in range(1, self.num_in_q + 1):
            self.time_arrival[i] = self.time_arrival[i + 1]
            self.service_type_arrival[i] = self.service_type_arrival[i + 1]


    def report(self):
        print("\n--- Estadísticas Generales ---")
        print("Average delay in queue:", self.total_of_delays / self.num_custs_delayed)
        print("Average number in queue:", self.area_num_in_q / self.sim_time)
        print("Server utilization:", self.area_server_status/self.sim_time)
        print("Total simulation time:", self.sim_time)
        print("Time server can depart since store closes: ", max(0, self.sim_time - self.time_limit))
        print("Total income: ", self.area_total_income)
        print("Total sales per client", self.area_total_income / self.num_custs_delayed)
        
        print("\n--- Estadísticas por Tipo de Servicio ---")
        service_names = {
            self.SERVICE_A: "Servicio A (Uniforme)",
            self.SERVICE_B: "Servicio B (Exponencial)",
            self.NO_SERVICE: "Sin Servicio"
        }
        
        for service_type in [self.SERVICE_A, self.SERVICE_B, self.NO_SERVICE]:
            count = self.service_counts[service_type]
            if count > 0:
                print(f"\n{service_names[service_type]}:")
                print(f"  Clientes atendidos: {int(count)}")
                print(f"  Tiempo total de servicio: {self.service_times[service_type]:.2f}")
                print(f"  Tiempo promedio de servicio: {self.service_times[service_type]/count:.2f}")
                print(f"  Tiempo total en cola: {self.queue_times[service_type]:.2f}")
                print(f"  Tiempo promedio en cola: {self.queue_times[service_type]/count:.2f}")
                print(f"  Proporción de clientes: {count/self.num_custs_delayed:.2%}")
                print(f"  Ventas totales: ${self.sales_by_service[service_type]:.2f}")
            else:
                print(f"\n{service_names[service_type]}: No hubo clientes de este tipo")
        
    def update_time_avg_stats(self):
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_status * time_since_last_event

    def main(self):
    self.num_events = 2
    print("Single Server Queue Simulation\n\n")
    print("Mean interarrival time: ", self.mean_interarrival)
    self.initialize()
    while (self.sim_time < self.time_limit) or (self.num_in_q > 0):
        if self.sim_time >= self.time_limit:
            self.store_status = self.CLOSED
            self.time_next_event[1] = float('inf')
        self.timing()
        self.update_time_avg_stats()
        if self.next_event_type == 1:
            self.arrive()
        else:
            self.depart()
    self.report()

if __name__ == "__main__":
    params = {
        'mean_interarrival': 3.0,
        'mean_service_A_inf': 3.1,
        'mean_service_A_sup': 3.8,
        'mean_service_B': 7.0,
        'mean_no_service_': 1.5,
        'prob_service_A': 0.5,
        'prob_service_B': 0.3,
        'num_delays_required': 1000,
        'time_limit': 480.0,
        'sales_A': 2500,
        'sales_B': 4000,
        'sales_no_service': 0
    }
    simulator = SimuladorAlmacen(params)
    simulator.main()