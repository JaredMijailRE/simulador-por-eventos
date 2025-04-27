# from numba import jit
import numpy as np
# import matplotlib.pyplot as plt

import numpy as np
import math

def normal_polar():
  "Crea pares de valores aleatorios de una normal estándar usando el método polar de Box-Muller"
  while True:
    v1 = 2 * np.random.rand() - 1
    v2 = 2 * np.random.rand() - 1
    w = v1**2 + v2**2
    if 0 < w <= 1:
      break
  y = math.sqrt(-2 * math.log(w) / w)
  x0 = v1 * y
  x1 = v2 * y
  return x0, x1

clients = []
num_samples = 5
for i in range(num_samples):
    rand1, rand2 = normal_polar()
    clients.append(rand1*10)
    clients.append(rand2*10)



print(clients)
  
