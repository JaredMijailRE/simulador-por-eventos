from numba import jit
import random

@jit(nopython=True)
def random_variable_5():
    u = random.random()  # Uniform [0.0, 1.0)
    if u <= 3/5:
        return 5 * u
    else:
        return 15 * u - 6

# Example usage
if __name__ == "__main__":
    # Generate 10 random variables
    samples = [random_variable_5() for _ in range(10)]
    print(samples)


  
