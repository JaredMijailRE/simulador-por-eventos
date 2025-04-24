from numba import jit
import numpy as np
import matplotlib.pyplot as plt


@jit(nopython=True)
def inverse_cdf_triangular(a, b, c):
    u = np.random.random()
    Fc = (c - a) / (b - a)
    if u < Fc:
        return a + np.sqrt(u * (b - a) * (c - a))
    else:
        return b - np.sqrt((1 - u) * (b - a) * (b - c))

def simulation(n, funcion):
    result = np.empty(n, dtype=np.float64)
    for i in range(n):
        result[i] = funcion()
    return result

a = 8 # inicio del triangulo
b = 10 # fin del triangulo
c = 9 # pico del triangulo

result = simulation(100000000, lambda: inverse_cdf_triangular(a, b, c))
print("Simulación de 100,000,000 muestras de la distribución triangular:")
print(result[:10]) 

plt.hist(result, bins=1000, density=True)
plt.title("Distribución Triangular: Simulada vs Teórica")
plt.xlabel("x")
plt.ylabel("Densidad")

plt.show()