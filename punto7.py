import numpy as np
import math

Q_LIMIT = 1000
BUSY = 0
IDLE = 1
time_arrival=[]
time_next_event=[]
int(next_event_type) = 0
int(num_custs_delayed) = 0
int(num_delays_required) = 0
int(num_events) = 2
int(num_in_q) = 0
int(server_status) = 0
float(mean_interarrival) = 10.0
float(mean_service) = 60.0
float(sim_time) = 0.0
float(time_arrival[Q_LIMIT])
float(time_last_event) = 0.0
float(time_next_event[3])
float(total_of_delays) = 0.0
float(area_server_status) = 0.0
mean_interarrival = 10.0

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
   for (i=1, i<=num_events, ++i):
    
        
        









