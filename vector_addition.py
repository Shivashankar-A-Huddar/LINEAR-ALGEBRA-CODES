import numpy as np

# Defining vectors
vector_a = np.array([1, 2, 3])
vector_b = np.array([4, 5, 6])

# Vector addition
addition = np.add(vector_a, vector_b)

# Vector subtraction
subtraction = np.subtract(vector_a, vector_b)

# Scalar multiplication
scalar_multiplication = 2 * vector_a

# Display results
print("Vector A:", vector_a)
print("Vector B:", vector_b)
print("Addition:", addition)
print("Subtraction:", subtraction)
print("Scalar Multiplication (2 * A):", scalar_multiplication)

# Output:
# Vector A: [1 2 3]
# Vector B: [4 5 6]
# Addition: [5 7 9]
# Subtraction: [-3 -3 -3]
# Scalar Multiplication (2 * A): [2 4 6]

