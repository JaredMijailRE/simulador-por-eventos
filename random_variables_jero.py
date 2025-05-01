# from numba import jit
import numpy as np
# import matplotlib.pyplot as plt

import numpy as np
import math

def exponential(beta):
  u = np.random.rand()
  return -beta*np.log(u)

clients = []
num_samples = 5
for i in range(num_samples):
    rand = exponential(10)
    clients.append(rand)

print(type(clients[0]))
  
