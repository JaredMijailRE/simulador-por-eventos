import numpy as np

class SimuladorAlmacen:
    def __init__(self, params):
        self.QLIMIT = params['num_delays_required']
        self.BUSY = 1
        self.IDLE = 0
        self.next_event_type = 0
        self.num_custs_delayed = 0
        self.num_delays_required = params['num_delays_required']
        self.num_events = 0
        self.num_in_q = 0
        self.server_status = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.mean_interarrival = params['mean_interarrival']
        self.mean_service = params['mean_service']
        self.sim_time = 0.0
        self.time_arrival = np.zeros(self.QLIMIT + 1)
        self.time_last_event = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)  
        self.total_of_delays = 0.0

    @staticmethod
    def exponential(beta):
            """Genera un número aleatorio con distribución exponencial."""
            u = np.random.rand()
            return -beta * np.log(u)
        
    def initialize(self):
        self.sim_time = 0.0
        self.server_status = self.IDLE
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_next_event = [0.0] * (self.num_events + 1)  
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        self.time_next_event[2] = float('inf')
        
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
        self.sim_time = min_time_next_event

    def arrive(self):
        self.time_next_event[1] = self.sim_time + self.exponential(self.mean_interarrival)
        if self.server_status == self.BUSY:
            self.num_in_q += 1
            if self.num_in_q > self.QLIMIT:
                print("Overflow of the queue at time", self.sim_time)
            else:
                self.time_arrival[self.num_in_q] = self.sim_time
        else:
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status = self.BUSY
            self.time_next_event[2] = self.sim_time + self.exponential(self.mean_service)
        
    def depart(self):
        delay = 0
        if self.num_in_q == 0:
            self.server_status = self.IDLE
            self.time_next_event[2] = float('inf')
        else:
            self.num_in_q -= 1
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.time_next_event[2] = self.sim_time + self.exponential(self.mean_service)
            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]

    def report(self):
        print("Average delay in queue:", self.total_of_delays / self.num_custs_delayed)
        print("Average number in queue:", self.area_num_in_q / self.sim_time)
        print("Server utilization:", self.area_server_status/self.num_custs_delayed)
        print("Total simulation time:", self.sim_time)
        
    def update_time_avg_stats(self):
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_status * time_since_last_event

    def main(self):
        self.num_events = 2
        print("Single Server Queue Simulation\n\n")
        print("Mean interarrival time: ", self.mean_interarrival)
        print("Mean service time: ", self.mean_service)
        print("Number of customers to be served: ", self.num_delays_required)
        self.initialize()
        while self.num_custs_delayed < self.num_delays_required:
            self.timing()
            self.update_time_avg_stats()
            if self.next_event_type == 1:
                self.arrive()
            else:
                self.depart()
        self.report()

if __name__ == "__main__":
    # Parámetros: tiempo entre llegadas, tiempo servicio1, tiempo servicio2, prob servicio1, clientes requeridos
    params = {
        'mean_interarrival': 1.0,
        'mean_service': 0.5,
        'num_delays_required': 1000
    }
    simulator = SimuladorAlmacen(params)
    simulator.main()              