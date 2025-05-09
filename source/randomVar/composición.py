import math
import random
import numpy as np
import matplotlib.pyplot as plt

def triangular_comp():
    U = random.random()
    if U < 0.5:
        H = U / 0.5
        Δ = (-1 + math.sqrt(1 + 8 * H)) / 2
        return 8 + Δ
    else:
        H = (U - 0.5) / 0.5
        Δ = (3 - math.sqrt(9 - 8 * H)) / 2
        return 9 + Δ

def trapezoidal_comp(a, b, c):
    h = 2.0 / (b - a + c)
    A1 = a * h / 2
    A2 = (b - a) * h
    A3 = (c - b) * h / 2
    U = random.random()
    if U < A1:
        W = U / A1
        return a * math.sqrt(W)
    elif U < A1 + A2:
        return a + (U - A1) / h
    else:
        V = (U - A1 - A2) / A3
        return c - (c - b) * math.sqrt(1 - V)

# Generar muestras
N = 200_000
samples_tri = np.array([triangular_comp() for _ in range(N)])
samples_trap = np.array([trapezoidal_comp(2,5,8) for _ in range(N)])


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), sharex=False)

# Triangular
ax1.hist(samples_tri, bins=200, density=True, alpha=0.7, color='skyblue', edgecolor='none')
ax1.set_xlim(7.5, 10.5)
ax1.set_ylim(0, 0.9)
ax1.set_title("Triangular")
ax1.set_ylabel("Densidad")
ax1.grid(True, linestyle='--', linewidth=0.5)

# Trapezoidal
ax2.hist(samples_trap, bins=200, density=True, alpha=0.7, color='skyblue', edgecolor='none')
ax2.set_xlim(-1, 9)
ax2.set_ylim(0, 0.22)
ax2.set_title("Trapezoidal")
ax2.set_xlabel("x")
ax2.set_ylabel("Densidad")
ax2.grid(True, linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()