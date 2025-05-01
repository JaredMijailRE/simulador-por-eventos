import numpy as np

class SimuladorCafeteria:
    def __init__(self, mean_interarrival, mean_service, num_delays_required):
        # Constantes
        self.Q_LIMIT = num_delays_required
        self.BUSY = 0
        self.IDLE = 1

        # Parámetros de simulación
        self.mean_interarrival = mean_interarrival
        self.mean_service = mean_service
        self.num_delays_required = num_delays_required
        self.num_events = 2

        # Estado de la simulación
        self.sim_time = 0.0
        self.server_status = self.IDLE
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)  # Índices 0, 1, 2
        self.time_arrival = [0.0] * (self.Q_LIMIT + 1)  # Tamaño Q_LIMIT + 1
        self.simulation_stopped = False

    @staticmethod
    def exponential(beta):
        """Genera un número aleatorio con distribución exponencial."""
        u = np.random.rand()
        return -beta * np.log(u)

    def initialize(self):
        """Inicializa el estado de la simulación."""
        self.sim_time = 0.0
        self.server_status = self.IDLE
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        self.time_next_event[2] = float("inf")
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

    def arrive(self):
        """Procesa la llegada de un cliente."""
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)

        if self.server_status == self.BUSY:
            self.num_in_q += 1
            if self.num_in_q > self.Q_LIMIT:
                print("Límite de cola alcanzado en el tiempo:", self.sim_time)
                print("Deteniendo la simulación y generando reporte...")
                self.simulation_stopped = True
                return
            self.time_arrival[self.num_in_q] = self.sim_time
        else:
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status = self.BUSY
            self.time_next_event[2] = self.sim_time + self.exponential(self.mean_service)

    def depart(self):
        """Procesa la salida de un cliente."""
        if self.num_in_q == 0:
            self.server_status = self.IDLE
            self.time_next_event[2] = float("inf")
        else:
            self.num_in_q -= 1
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.time_next_event[2] = self.sim_time + self.exponential(self.mean_service)

            # Reorganizar la cola
            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]

    def update_time_avg_stats(self):
        """Actualiza las estadísticas de tiempo promedio."""
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_status * time_since_last_event

    def report(self):
        """Genera el reporte final de la simulación."""
        print("\n--- Reporte Final ---")
        print("Tiempo de simulación:", self.sim_time)
        print("Número de clientes atendidos:", self.num_custs_delayed)
        print("Tiempo promedio en cola:", self.total_of_delays / self.num_custs_delayed)
        print("Tiempo promedio en el sistema:", (self.total_of_delays / self.num_custs_delayed) + self.mean_service)
        print("Porcentaje de tiempo que el servidor estuvo ocupado:", (self.area_server_status / self.sim_time) * 100.0)
        print("Porcentaje de tiempo que la cola estuvo ocupada:", (self.area_num_in_q / self.sim_time) * 100.0)

    def main(self):
        """Ejecuta la simulación completa."""
        self.initialize()

        while self.num_custs_delayed < self.num_delays_required and not self.simulation_stopped:
            next_event_type = self.timing()
            self.update_time_avg_stats()

            if next_event_type == 1:
                self.arrive()
            elif next_event_type == 2:
                self.depart()
            else:
                print("Evento no reconocido")
                self.simulation_stopped = True
                break

        self.report()

# Ejecutar la simulación
if __name__ == "__main__":
    simulator = SimuladorCafeteria(mean_interarrival=10.0, mean_service=60.0, num_delays_required=1000)
    simulator.main()