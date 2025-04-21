import numpy as np
import numba

@numba.jit
def densidad1(x):
    """
    Funcin de densidad definida por dos partes por dos rectas
    """
    if 0.0 <= x <= 0.5:
        return 2 * x + 15 / 2
    elif 0.5 < x <= 1.0:
        return -2 * x + 21 / 2
    else:
        return -1  
    
@numba.jit
def densidad2(x):
    pass
    
@numba.jit
def densidad3(x):
    if 0 <= x <= 0.5:
        return 3/4
    elif 0.5 < x <= 1.0:
        return 1/4
    else:
        return 0
    
@numba.jit
def densidad4(x):
    pass

@numba.jit
def transformada_inversa1(densidad, n=1):
    """
    Genera una muestra aleatoria de la transformada inversa
    de la función densidad 1 que descubre una funcion triangular
    """
    resultados = np.empty(n)
    for i in range(n):
        u = np.random.uniform(0.0, 1.0)
        resultados[i] = densidad(u)
    return resultados if n > 1 else resultados[0]


    

