import numpy as np

class SimuladorAlmacen:
    def __init__(self, params):
        # Variables de simulación, incluyendo etiquetas para estados del servidor o de la tienda
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
        self.server_status = []
        # Número de servidores del simulador
        self.num_servers = params.get('num_servers', 1) 
        self.store_status = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        #Cálculo de ingresos diarios
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
        self.time_next_event = []
        self.total_of_delays = 0.0
        self.service_counts = np.zeros(self.num_service_types + 1)
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
    
    @staticmethod
    def exponential(beta):
        'Genera un número aleatorio exponencial con parámetro beta.'
        u = np.random.rand()
        return -beta * np.log(u)

    def select_service(self):
        'Selecciona el tipo de servicio basado en las probabilidades definidas.'
        u = np.random.rand()
        if u < self.prob_service_A:
            return self.SERVICE_A
        elif u < self.prob_service_A + self.prob_service_B:
            return self.SERVICE_B
        else:
            return self.NO_SERVICE
        
    def service_time(self, service_type):
        'Calcula el tiempo de servicio basado en el tipo de servicio proporcionado.'
        if service_type == self.SERVICE_A:
            v = np.random.rand()
            return v * (self.mean_service_A_sup - self.mean_service_A_inf) + self.mean_service_A_inf
        elif service_type == self.SERVICE_B:
            return self.exponential(self.mean_service_B)
        elif service_type == self.NO_SERVICE:
            return self.mean_no_service
        else:
            print("Error: Tipo de servicio inválido", service_type)
            return 0.0
        
    def sales(self, service_type):
        'Calcula las ventas basadas en el tipo de servicio proporcionado.'
        if service_type == self.SERVICE_A:
            return self.sales_A
        elif service_type == self.SERVICE_B:
            return self.sales_B
        elif service_type == self.NO_SERVICE:
            return self.sales_no_service
        else:
            print("Error: Tipo de servicio inválido", service_type)
            return 0.0
        
    def initialize(self):
        'Inicializa las variables de la simulación.'
        self.sim_time = 0.0
        self.server_status = [self.IDLE] * self.num_servers #1 por cada servidor
        self.store_status = self.OPEN
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.area_total_income = 0.0
        self.num_events = 1 + self.num_servers  # Eventos: 1 llegada + num_servers salidas
        self.time_next_event = [0.0] * (self.num_events + 1)
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        for i in range(2, self.num_events + 1):
            self.time_next_event[i] = float('inf') #Tiempo de salida por defecto
        self.service_counts = np.zeros(self.num_service_types + 1)
        self.service_times = np.zeros(self.num_service_types + 1)
        self.queue_times = np.zeros(self.num_service_types + 1)
        self.sales_by_service = np.zeros(self.num_service_types + 1)
        self.service_type_arrival = np.zeros(self.QLIMIT + 1)
        
    def timing(self):
        'Determina el próximo evento a procesar.'
        min_time_next_event = float('inf')
        self.next_event_type = 0
        for i in range(1, self.num_events + 1): #Encuentra el próximo evento
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i
        if self.next_event_type == 0:
            print("Lista de eventos vacía en tiempo", self.sim_time)
            return
        if min_time_next_event > self.time_limit: #Detecta cuando se cierra la tienda, evitando nuevas llegadas
            self.store_status = self.CLOSED
        # Permite que los clientes que estaban haciendo fila en el cierre sean atendidos
        self.sim_time = min_time_next_event

    def arrive(self):
        'Manejo de evento de llegada del cliente'
        if self.store_status == self.OPEN: #Solo agenda proxima llegada si la tienda está abierta
            self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        else:
            self.time_next_event[1] = float('inf')
        #Decide tipo de cliente
        service_type = self.select_service()
        #Encuentra servidores libres
        available_server = next((i for i, status in enumerate(self.server_status) if status == self.IDLE), None)
        
        if available_server is not None: #Inicio de servicio
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status[available_server] = self.BUSY #Ocupa el servidor que aceptó al cliente
            service_time = self.service_time(service_type)
            departure_event = 2 + available_server #Manejo interno de arreglo de eventos
            self.time_next_event[departure_event] = self.sim_time + service_time
            self.service_counts[service_type] += 1
            self.service_times[service_type] += service_time
            sale_amount = self.sales(service_type)
            self.sales_by_service[service_type] += sale_amount
            self.area_total_income += sale_amount
        else:
            self.num_in_q += 1
            if self.num_in_q > self.QLIMIT: #Condicional incluido para evitar atascos indefinidos
                print("Overflow de la cola en tiempo", self.sim_time)
            else:
                self.time_arrival[self.num_in_q] = self.sim_time
                self.service_type_arrival[self.num_in_q] = service_type

    def depart(self):
        'Manejo de los eventos de salida'
        server_index = self.next_event_type - 2 #Indica servidor que termina servicio
        if self.num_in_q > 0:
            service_type = int(self.service_type_arrival[1])
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            service_time = self.service_time(service_type)
            self.time_next_event[self.next_event_type] = self.sim_time + service_time
            self.service_counts[service_type] += 1
            self.service_times[service_type] += service_time
            self.queue_times[service_type] += delay
            sale_amount = self.sales(service_type)
            self.sales_by_service[service_type] += sale_amount #Se calculan los ingresos al terminar el servicio
            self.area_total_income += sale_amount
            self.num_in_q -= 1
            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]
                self.service_type_arrival[i] = self.service_type_arrival[i + 1]
        else:
            self.server_status[server_index] = self.IDLE
            self.time_next_event[self.next_event_type] = float('inf')

    def update_time_avg_stats(self):
        'Actualización de estadísticas por cada evento'
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        busy_servers = sum(status == self.BUSY for status in self.server_status)
        self.area_server_status += busy_servers * time_since_last_event

    def report(self):
        'Generador del reporte'
        print("\n--- Estadísticas Generales ---")
        print("Demora promedio en cola:", self.total_of_delays / self.num_custs_delayed)
        print("Número promedio en cola:", self.area_num_in_q / self.sim_time)
        print("Utilización del servidor:", self.area_server_status / (self.num_servers * self.sim_time))
        print("Tiempo total de simulación:", self.sim_time)
        print("Tiempo desde cierre hasta último cliente:", max(0, self.sim_time - self.time_limit))
        print("Ingresos totales:", self.area_total_income)
        print("Venta promedio por cliente:", self.area_total_income / self.num_custs_delayed)
        
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
                print(f"\n{service_names[service_type]}: Sin clientes")

    def main(self):
        print("Simulación de Cola con Múltiples Servidores\n\n")
        self.initialize()
        while self.sim_time < self.time_limit or self.num_in_q > 0 or any(status == self.BUSY for status in self.server_status):
            # Programa normal ejecuta mientras la tienda esté abierta, o cerrada con clientes pendientes
            self.timing()
            if self.sim_time > self.time_limit:
                self.store_status = self.CLOSED
                self.time_next_event[1] = float('inf')
            self.update_time_avg_stats()
            if self.next_event_type == 1:
                self.arrive()
            elif 2 <= self.next_event_type <= self.num_events:
                self.depart()
        self.report()

if __name__ == "__main__":
    params = {
        'num_servers': 2,  # Ejemplo: 2 servidores
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