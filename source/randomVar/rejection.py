# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from numba import jit
import numpy as np
import matplotlib.pyplot as plt

# Metodo de rechazo
@jit(nopython=True)
def rejection_Method(target_pdf, proposal_sampler, M) -> float:
    while True:
        x = proposal_sampler()
        u = np.random.random()
        if u < target_pdf(x) / M:
            return x

# Generacion de muestras
def sampling(n_Samples, func) -> np.ndarray:
    samples = np.empty(n_Samples)
    for i in range(n_Samples):
        samples[i] = func()
    return samples

# Graficacion
def rej_Make_Graph(samples,title) -> None:
    plt.figure(figsize=(10, 5))
    plt.hist(samples, bins=1000, density=True, alpha=0.7, color='skyblue')
    plt.title(title)
    plt.xlabel('x')
    plt.ylabel('Densidad')
    plt.grid(True)
    plt.show()

# Ejemplos especificos (para cada uno hay que definir funcion objetivo, funcion propuesta y cota M)
if __name__ == '__main__':
    # Distribucion de la tercera grafica
    @jit(nopython=True)
    def target_pdf_c(x) -> float:
        if 0 <= x < 1:
            return 0.75
        elif 1 <= x <= 2:
            return 0.25
        else:
            return 0.0

    # Se escoge una funcion propuesta uniforme adecuada
    @jit(nopython=True)
    def proposal_Sampler_c() -> float:
        return np.random.uniform(0, 2)

    M_c = 1.5   # Constante cota para la tercera grafica

    # Distribucion de la cuarta grafica
    @jit(nopython=True)
    def target_pdf_d(x) -> float:
        if 4 <= x < 5:
            return 0.75 - 0.5 * (x - 4)
        elif 5 <= x <= 6:
            return 0.25 + 0.5 * (x - 5)
        else:
            return 0.0
        
    @jit(nopython=True)
    def proposal_Sampler_d() -> float:
        return np.random.uniform(4, 6)

    M_d = 1.5

    # Generando muestras experimentales
    n_Samples = 1000000
    samples_c = sampling(n_Samples, lambda: rejection_Method(target_pdf_c, proposal_Sampler_c, M_c))
    print(samples_c[:10])
    samples_d = sampling(n_Samples, lambda: rejection_Method(target_pdf_d, proposal_Sampler_d, M_d))
    print(samples_d[:10])

    # Grafica 3
    rej_Make_Graph(samples_c, "Distribución C: Muestras Simuladas")

    # Grafica 4
    rej_Make_Graph(samples_d, "Distribución D: Muestras Simuladas")
