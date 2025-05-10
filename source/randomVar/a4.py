import random
import math
import matplotlib.pyplot as plt
from numba import njit


@njit
def generador_variable_aleatoria_continua():
    u = random.uniform(0, 1)
    x = 0
    if 0 < u <= 0.5:
        x = 6 * u - 3
    elif 0.5 < u <= 1:
        x = math.sqrt(32 * (u - 0.5))
    
    if u == 0:
        x = -3
    elif u == 1:
        x = 4
        
    return x

if __name__ == "__main__":
    num_muestras = 10000000
    muestras_generadas = [generador_variable_aleatoria_continua() for _ in range(num_muestras)]

    plt.figure(figsize=(10, 6))
    plt.hist(muestras_generadas, bins=1000, density=True, edgecolor='black', alpha=0.7, label='Histograma Muestras')
    plt.title(f'Histograma de {num_muestras} Muestras Generadas y PDF Teórica')
    plt.xlabel('Valor de la Variable Aleatoria X')
    plt.ylabel('Densidad')
    plt.grid(axis='y', alpha=0.75)
    
    segmento1_x = [-3, 0]
    segmento1_y = [1/6, 1/6]
    
    segmento2_x_vals = []
    current_x = 0.001
    while current_x <= 4:
        segmento2_x_vals.append(current_x)
        current_x += 0.01
    if not segmento2_x_vals or segmento2_x_vals[-1] < 4:
         segmento2_x_vals.append(4)

    segmento2_y_vals = [x_val/16 for x_val in segmento2_x_vals]
    
    plt.plot(segmento1_x, segmento1_y, color='red', linestyle='--', linewidth=2, label='PDF Teórica (-3<x<=0): 1/6')
    
    # Adjusting plot for the second segment to connect to the y-axis at x=0 from the right
    if segmento2_x_vals:
      plt.plot([0] + segmento2_x_vals, [0/16] + segmento2_y_vals, color='blue', linestyle='--', linewidth=2, label='PDF Teórica (0<x<=4): x/16')
    
    plt.axvline(x=-3, color='gray', linestyle=':', linewidth=1)
    plt.axvline(x=0, color='gray', linestyle=':', linewidth=1)
    plt.axvline(x=4, color='gray', linestyle=':', linewidth=1)
    
    plt.legend()
    plt.show()