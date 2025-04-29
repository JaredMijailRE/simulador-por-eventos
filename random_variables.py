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

def makeGraph(result):
    plt.hist(result, bins=1000, density=True)
    plt.title("Distribución")
    plt.xlabel("x")
    plt.ylabel("Densidad")

    plt.show()

@jit(nopython=True)
def inverse_cdf_trapezoidal( a, b, c, d):
    u = np.random.random()
    
    h = 2 / (d + c - a - b)

    A1 = (b - a) * h / 2
    A2 = (c - b) * h
    A3 = (d - c) * h / 2

    if u < A1:
        return a + np.sqrt((2 * u * (b - a)) / h)
    elif u < A1 + A2:
        return b + (u - A1) / h
    elif u <= 1.0:
        z = u - A1 - A2
        return d - np.sqrt((2 * (A3 - z) * (d - c)) / h)
    else:
        raise ValueError("u debe estar en el intervalo [0, 1]")
    
d = 7
result = simulation(100000000, lambda: inverse_cdf_trapezoidal(d, a, c, b))
makeGraph(result)