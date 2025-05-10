import numpy as np

def triangular_custom_rvs(n=10, seed=None):
    if seed is not None:
        np.random.seed(seed)
    U = np.random.uniform(0, 1, n)
    X = np.where(
        U <= 0.25,
        2 + 2 * np.sqrt(U),
        6 - np.sqrt(12 * (1 - U))
    )
    return X

# Generar 10 valores
samples = triangular_custom_rvs(10, seed=42)
sample_mean = np.mean(samples)

# Imprimir
print("Valores generados:", samples)
print("Media muestral:", sample_mean)
