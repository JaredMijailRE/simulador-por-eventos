from numba import jit
import numpy as np
import matplotlib.pyplot as plt
import random

@jit(nopython=True)
def random_variable_5():
    u = random.random() 
    if u <= 3/5:
        return 5 * u
    else:
        return 15 * u - 6

@jit(nopython=True)
def simulation(n, funcion):
    result = np.empty(n, dtype=np.float64)
    for i in range(n):
        result[i] = funcion()
    return result

def makeGraph(result):
    plt.hist(result, bins=50, density=True)  # Reduje bins a 50 para mejor visualización
    plt.title("Distribución")
    plt.xlabel("x")
    plt.ylabel("Densidad")
    plt.show()

# Ejemplo de uso
if __name__ == "__main__":
    # Generar 1000 muestras
    result = simulation(1000, random_variable_5)
    print("Simulación de 1000 muestras de la distribución triangular:")
    print(result[:10])
    
    # Generar 10 muestras adicionales para demostración
    samples = [random_variable_5() for _ in range(10)]
    print("\n10 muestras adicionales:")
    print(samples)
    
    # Mostrar el gráfico
    makeGraph(result)