import numpy as np

class SimuladorCafeteria:
    def __init__(self, mean_interarrival, mean_service1, mean_service2, prob_service1, num_delays_required):
        # Constantes
        self.Q_LIMIT = num_delays_required
        self.BUSY = 1
        self.IDLE = 0
        self.SERVICE1 = 1
        self.SERVICE2 = 2
        self.SERVERS_SERVICE1 = 6  # 6 servidores para el servicio 1
        self.SERVERS_SERVICE2 = 1  # 1 servidor para el servicio 2

        # Parámetros de simulación
        self.mean_interarrival = mean_interarrival
        self.mean_service1 = mean_service1  # Tiempo de servicio para cola 1
        self.mean_service2 = mean_service2  # Tiempo de servicio para cola 2
        self.prob_service1 = prob_service1  # Probabilidad de elegir servicio 1
        self.num_delays_required = num_delays_required
        self.num_events = 2 + self.SERVERS_SERVICE1 + self.SERVERS_SERVICE2  # Llegada + salidas

        # Estado de la simulación
        self.sim_time = 0.0
        # Estado de los servidores: lista para servicio1 (6 servidores) y servicio2 (1 servidor)
        self.server_status = [[self.IDLE] * self.SERVERS_SERVICE1, [self.IDLE] * self.SERVERS_SERVICE2]
        self.num_in_q = [0, 0]  # Número en cada cola
        self.time_last_event = 0.0
        self.num_custs_delayed = [0, 0]  # Clientes atendidos por cada servicio
        self.total_of_delays = [0.0, 0.0]  # Tiempo total en cola por servicio
        self.area_num_in_q = [0.0, 0.0]  # Área bajo Q(t) para cada cola
        self.area_server_status = [0.0, 0.0]  # Suma de tiempos ocupados para cada grupo de servidores
        # Índices: 0 no usado, 1=llegada, 2+=salidas (primero servicio1, luego servicio2)
        self.time_next_event = [0.0] * (self.num_events + 1)  
        self.time_arrival = [[0.0] * (self.Q_LIMIT + 1) for _ in range(2)]  # Colas separadas
        self.simulation_stopped = False

    @staticmethod
    def exponential(beta):
        """Genera un número aleatorio con distribución exponencial."""
        u = np.random.rand()
        return -beta * np.log(u)

    def initialize(self):
        """Inicializa el estado de la simulación."""
        self.sim_time = 0.0
        self.server_status = [[self.IDLE] * self.SERVERS_SERVICE1, [self.IDLE] * self.SERVERS_SERVICE2]
        self.num_in_q = [0, 0]
        self.time_last_event = 0.0
        self.num_custs_delayed = [0, 0]
        self.total_of_delays = [0.0, 0.0]
        self.area_num_in_q = [0.0, 0.0]
        self.area_server_status = [0.0, 0.0]
        
        # Inicializar eventos de llegada y salida
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)  # Llegada
        
        # Inicializar todos los eventos de salida como infinito (servidores ociosos)
        for i in range(2, self.num_events + 1):
            self.time_next_event[i] = float("inf")
            
        self.simulation_stopped = False

    def timing(self):
        """Determina el próximo evento a ejecutar."""
        min_time_next_event = float("inf")
        next_event_type = 0

        for i in range(1, self.num_events + 1):
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                next_event_type = i

        if next_event_type == 0:
            print("Lista de eventos vacía en el tiempo:", self.sim_time)
            self.simulation_stopped = True
            return None

        self.sim_time = min_time_next_event
        return next_event_type

    def find_idle_server(self, service_type):
        """Encuentra un servidor ocioso para el servicio especificado."""
        service_idx = 0 if service_type == self.SERVICE1 else 1
        servers = self.server_status[service_idx]
        
        for i in range(len(servers)):
            if servers[i] == self.IDLE:
                return i
        return -1

    def arrive(self):
        """Procesa la llegada de un cliente."""
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)

        # Decidir a qué servicio va el cliente
        if np.random.rand() < self.prob_service1:
            service_type = self.SERVICE1
            service_idx = 0  # Índice para servicio1
        else:
            service_type = self.SERVICE2
            service_idx = 1  # Índice para servicio2

        # Buscar un servidor ocioso
        server_id = self.find_idle_server(service_type)
        
        if server_id == -1:  # Todos los servidores ocupados
            self.num_in_q[service_idx] += 1
            if self.num_in_q[service_idx] > self.Q_LIMIT:
                print(f"\n¡Advertencia! Límite de cola {service_type} alcanzado en el tiempo:", self.sim_time)
                print("Deteniendo la simulación y generando reporte...")
                self.simulation_stopped = True
                return
            self.time_arrival[service_idx][self.num_in_q[service_idx]] = self.sim_time
        else:
            delay = 0.0
            self.total_of_delays[service_idx] += delay
            self.num_custs_delayed[service_idx] += 1
            self.server_status[service_idx][server_id] = self.BUSY
            
            # Programar evento de salida
            if service_type == self.SERVICE1:
                # El índice 2-7 son los servidores del servicio1 (6 servidores)
                self.time_next_event[2 + server_id] = self.sim_time + self.mean_service1
            else:
                # El índice 8 es el único servidor del servicio2
                self.time_next_event[2 + self.SERVERS_SERVICE1 + server_id] = self.sim_time + self.mean_service2

    def depart(self, event_type):
        """Procesa la salida de un cliente de un servidor específico."""
        # Determinar a qué servicio pertenece el servidor
        if 2 <= event_type <= 1 + self.SERVERS_SERVICE1:  # Servicio1
            service_type = self.SERVICE1
            service_idx = 0
            server_id = event_type - 2
        else:  # Servicio2
            service_type = self.SERVICE2
            service_idx = 1
            server_id = event_type - 2 - self.SERVERS_SERVICE1
        
        # Verificar si hay clientes en la cola
        if self.num_in_q[service_idx] == 0:
            self.server_status[service_idx][server_id] = self.IDLE
            self.time_next_event[event_type] = float("inf")
        else:
            self.num_in_q[service_idx] -= 1
            delay = self.sim_time - self.time_arrival[service_idx][1]
            self.total_of_delays[service_idx] += delay
            self.num_custs_delayed[service_idx] += 1
            
            # Programar próximo evento de salida para este servidor
            if service_type == self.SERVICE1:
                self.time_next_event[event_type] = self.sim_time + self.mean_service1
            else:
                self.time_next_event[event_type] = self.sim_time + self.mean_service2

            # Reorganizar la cola correspondiente
            for i in range(1, self.num_in_q[service_idx] + 1):
                self.time_arrival[service_idx][i] = self.time_arrival[service_idx][i + 1]

    def update_time_avg_stats(self):
        """Actualiza las estadísticas de tiempo promedio."""
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        
        # Actualizar estadísticas para ambas colas
        for i in range(2):
            self.area_num_in_q[i] += self.num_in_q[i] * time_since_last_event
            
            # Calcular número de servidores ocupados para este servicio
            busy_servers = sum(self.server_status[i])
            if i == 0:  # Servicio1
                self.area_server_status[i] += busy_servers * time_since_last_event
            else:  # Servicio2
                self.area_server_status[i] += busy_servers * time_since_last_event

    def report(self):
        """Genera el reporte final de la simulación."""
        print("\n--- Reporte Final ---")
        print(f"Tiempo de simulación: {self.sim_time:.2f} segundos")
        
        print("\n=== Servicio 1 (6 servidores) ===")
        print(f"Clientes atendidos: {self.num_custs_delayed[0]}")
        if self.num_custs_delayed[0] > 0:
            avg_delay = self.total_of_delays[0] / self.num_custs_delayed[0]
            print(f"Tiempo promedio en cola: {avg_delay:.2f} segundos")
            print(f"Tiempo promedio en el sistema: {avg_delay + self.mean_service1:.2f} segundos")
        else:
            print("Tiempo promedio en cola: No hay clientes atendidos")
        
        avg_busy = self.area_server_status[0] / self.sim_time
        print(f"Promedio de servidores ocupados: {avg_busy:.2f} de {self.SERVERS_SERVICE1}")
        print(f"Porcentaje de utilización: {(avg_busy / self.SERVERS_SERVICE1) * 100:.2f}%")
        print(f"Longitud promedio de cola: {self.area_num_in_q[0] / self.sim_time:.2f}")
        print(f"Estado final de la cola: {self.num_in_q[0]} clientes en cola")
        busy_servers = sum(self.server_status[0])
        print(f"Estado final de los servidores: {busy_servers} ocupados, {self.SERVERS_SERVICE1 - busy_servers} libres")
        
        print("\n=== Servicio 2 (1 servidor) ===")
        print(f"Clientes atendidos: {self.num_custs_delayed[1]}")
        if self.num_custs_delayed[1] > 0:
            avg_delay = self.total_of_delays[1] / self.num_custs_delayed[1]
            print(f"Tiempo promedio en cola: {avg_delay:.2f} segundos")
            print(f"Tiempo promedio en el sistema: {avg_delay + self.mean_service2:.2f} segundos")
        else:
            print("Tiempo promedio en cola: No hay clientes atendidos")
        
        avg_busy = self.area_server_status[1] / self.sim_time
        print(f"Porcentaje de tiempo ocupado: {avg_busy * 100:.2f}%")
        print(f"Longitud promedio de cola: {self.area_num_in_q[1] / self.sim_time:.2f}")
        print(f"Estado final de la cola: {self.num_in_q[1]} clientes en cola")
        print(f"Estado final del servidor: {'OCUPADO' if self.server_status[1][0] == self.BUSY else 'LIBRE'}")

    def main(self):
        """Ejecuta la simulación completa."""
        self.initialize()

        while (sum(self.num_custs_delayed) < self.num_delays_required and 
               not self.simulation_stopped):
            next_event_type = self.timing()
            if next_event_type is None:
                break
                
            self.update_time_avg_stats()

            if next_event_type == 1:  # Llegada
                self.arrive()
                if self.simulation_stopped:
                    break
            elif next_event_type >= 2:  # Salida de algún servidor
                self.depart(next_event_type)
            else:
                print("Evento no reconocido")
                self.simulation_stopped = True
                break

        self.report()

# Ejecutar la simulación
if __name__ == "__main__":
    # Parámetros: tiempo entre llegadas, tiempo servicio1, tiempo servicio2, prob servicio1, clientes requeridos
    simulator = SimuladorCafeteria(
        mean_interarrival=10.0, 
        mean_service1=60.0, 
        mean_service2=30.0, 
        prob_service1=0.8, 
        num_delays_required=1000
    )
    simulator.main()