import numpy as np
import math

Q_LIMIT = 1000
BUSY = 0
IDLE = 1
time_arrival=[]
time_next_event = []
next_event_type = 0
num_custs_delayed = 0
num_delays_required = 0
num_events = 2
num_in_q = 0
server_status = 0
mean_interarrival = 10.0
mean_service = 60.0
sim_time = 0.0
time_arrival[Q_LIMIT]
time_last_event = 0.0
time_next_event[3]
total_of_delays = 0.0
area_num_in_q = 0.0
area_server_status = 0.0

def exponential(beta):
  u = np.random.rand()
  return -beta*np.log(u)

def initialize():
    sim_time = 0.0
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0
    time_next_event[1] = sim_time + exponential(mean_interarrival)
    time_next_event[2] = float("inf")

def timing():
   i=0
   min_time_next_event = float("inf")
   next_event_type = 0
   for i in range(1, num_events + 1):
    if(time_next_event[i] < min_time_next_event):
        min_time_next_event = time_next_event[i]
        next_event_type = i
    if (next_event_type == 0):
        print("Lista de eventos vacía en el tiempo: ", sim_time)
        exit(1)
    sim_time = min_time_next_event

def arrive():
   delay = 0.0
   time_next_event[1] = sim_time + exponential(mean_interarrival)
   if server_status == BUSY:
      num_in_q += 1
      if num_in_q > Q_LIMIT:
         print("Limite de cola alcanzado en el tiempo: ", sim_time)
         exit(1)
      time_arrival[num_in_q] = sim_time
   else:
      delay = 0.0
      total_of_delays += delay
      num_custs_delayed += 1
      server_status = BUSY
      time_next_event[2] = sim_time + exponential(mean_service)

def depart():
   i=0
   delay = 0.0
   if num_in_q == 0:
      server_status = IDLE
      time_next_event[2] = float("inf")
   else:
      num_in_q -= 1
      delay = sim_time - time_arrival[1]
      total_of_delays += delay
      num_custs_delayed += 1
      time_next_event[2] = sim_time + exponential(mean_service)
      for i in range(1, num_in_q + 1):
         time_arrival[i] = time_arrival[i + 1]  

def report():
   print("Tiempo de simulación: ", sim_time)
   print("Número de clientes atendidos: ", num_custs_delayed)
   print("Tiempo promedio en cola: ", total_of_delays / num_custs_delayed)
   print("Tiempo promedio en el sistema: ", total_of_delays / num_custs_delayed + mean_service)
   print("Porcentaje de tiempo que el servidor estuvo ocupado: ", ((area_server_status) / sim_time * 100.0))
   print("Porcentaje de tiempo que la cola estuvo ocupada: ", (area_num_in_q / sim_time * 100.0))

def update_time_avg_stats():
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time
    area_num_in_q += num_in_q *  time_since_last_event
    area_server_status += server_status * time_since_last_event

def main():
    num_events = 2
    initialize()
    while (num_custs_delayed < num_delays_required):
        timing()
        update_time_avg_stats()
        switch(next_event_type):
            case 1:
                arrive()
                break
            case 2:
                depart()
                break
    report()
    return 0

