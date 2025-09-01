"""
Linear algebra operations for regression analysis.
Pure Python implementation without external dependencies.
"""

from __future__ import annotations
import math
from typing import List, Tuple, Union, Optional

Matrix = List[List[float]]
Vector = List[float]

def transpose(matrix: Matrix) -> Matrix:
    """Transpose a matrix."""
    if not matrix or not matrix[0]:
        return []
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def matrix_multiply(A: Matrix, B: Matrix) -> Matrix:
    """Multiply two matrices A * B."""
    if not A or not B or len(A[0]) != len(B):
        raise ValueError("Invalid matrix dimensions for multiplication")
    
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    
    result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    
    return result

def matrix_vector_multiply(A: Matrix, x: Vector) -> Vector:
    """Multiply matrix A by vector x."""
    if not A or not x or len(A[0]) != len(x):
        raise ValueError("Invalid dimensions for matrix-vector multiplication")
    
    result = []
    for row in A:
        result.append(sum(row[i] * x[i] for i in range(len(x))))
    
    return result

def vector_norm(v: Vector) -> float:
    """Compute the L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in v))

def vector_subtract(a: Vector, b: Vector) -> Vector:
    """Subtract vector b from vector a."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    return [a[i] - b[i] for i in range(len(a))]

def vector_add(a: Vector, b: Vector) -> Vector:
    """Add two vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    return [a[i] + b[i] for i in range(len(a))]

def scalar_vector_multiply(scalar: float, v: Vector) -> Vector:
    """Multiply a vector by a scalar."""
    return [scalar * x for x in v]

def dot_product(a: Vector, b: Vector) -> float:
    """Compute dot product of two vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same length")
    return sum(a[i] * b[i] for i in range(len(a)))

def householder_reflection(x: Vector) -> Tuple[Vector, float]:
    """
    Compute Householder reflection vector and beta for QR decomposition.
    Returns (v, beta) where H = I - beta * v * v^T
    """
    n = len(x)
    if n == 0:
        return [], 0.0
    
    # Compute norm and sign
    sigma = sum(x[i] * x[i] for i in range(1, n))
    v = [0.0] + x[1:]  # v[0] = 0 initially
    
    if sigma == 0.0 and x[0] >= 0:
        beta = 0.0
    elif sigma == 0.0 and x[0] < 0:
        beta = -2.0
    else:
        mu = math.sqrt(x[0] * x[0] + sigma)
        if x[0] <= 0:
            v[0] = x[0] - mu
        else:
            v[0] = -sigma / (x[0] + mu)
        
        beta = 2.0 * v[0] * v[0] / (sigma + v[0] * v[0])
        v = [vi / v[0] for vi in v]  # Normalize
    
    return v, beta

def apply_householder(A: Matrix, v: Vector, beta: float, start_col: int = 0) -> None:
    """Apply Householder transformation H = I - beta*v*v^T to matrix A in-place."""
    if beta == 0.0:
        return
    
    rows = len(A)
    cols = len(A[0]) if rows > 0 else 0
    
    for j in range(start_col, cols):
        # Compute w_j = v^T * A[:, j]
        w_j = sum(v[i] * A[i][j] for i in range(len(v)) if i < rows)
        
        # Apply transformation: A[:, j] = A[:, j] - beta * w_j * v
        for i in range(len(v)):
            if i < rows:
                A[i][j] -= beta * w_j * v[i]

def qr_decomposition(A: Matrix) -> Tuple[Matrix, Matrix]:
    """
    QR decomposition using Householder reflections.
    Returns (Q, R) where A = Q * R.
    """
    if not A or not A[0]:
        return [], []
    
    m, n = len(A), len(A[0])
    
    # Create copies for Q and R
    R = [row[:] for row in A]  # Copy of A
    Q = [[1.0 if i == j else 0.0 for j in range(m)] for i in range(m)]  # Identity matrix
    
    # Store Householder vectors and betas
    householder_data = []
    
    for k in range(min(m-1, n)):
        # Extract column vector from R
        x = [R[i][k] for i in range(k, m)]
        
        if not x:
            continue
            
        # Compute Householder reflection
        v, beta = householder_reflection(x)
        
        if beta != 0.0:
            # Extend v to full size
            v_full = [0.0] * k + v
            
            # Apply to R
            apply_householder(R, v_full, beta, k)
            
            # Store for Q computation
            householder_data.append((v_full, beta))
    
    # Construct Q by applying Householder transformations to identity
    for v_full, beta in reversed(householder_data):
        apply_householder(Q, v_full, beta, 0)
    
    # Transpose Q (since we built Q^T)
    Q = transpose(Q)
    
    return Q, R

def back_substitution(R: Matrix, b: Vector) -> Vector:
    """
    Solve Rx = b using back substitution, where R is upper triangular.
    R can be m x n where m >= n, but we only use the first n rows.
    """
    n = len(b)
    if n == 0:
        return []
    
    # Ensure R has at least n rows and n columns
    if len(R) < n or (len(R) > 0 and len(R[0]) < n):
        raise ValueError(f"Matrix R dimensions incompatible with vector b (R: {len(R)}x{len(R[0]) if R else 0}, b: {n})")
    
    x = [0.0] * n
    
    for i in range(n-1, -1, -1):
        if i >= len(R) or i >= len(R[i]):
            raise ValueError(f"Matrix index out of bounds: R[{i}][{i}]")
            
        if abs(R[i][i]) < 1e-12:
            raise ValueError(f"Matrix is singular at position ({i}, {i})")
        
        x[i] = b[i]
        for j in range(i+1, n):
            if j < len(R[i]):
                x[i] -= R[i][j] * x[j]
        x[i] /= R[i][i]
    
    return x

def solve_qr(Q: Matrix, R: Matrix, b: Vector) -> Vector:
    """
    Solve the linear system Ax = b using QR decomposition.
    A = QR, so x = R^(-1) * Q^T * b
    """
    # Compute Q^T * b
    Qt_b = matrix_vector_multiply(transpose(Q), b)
    
    # R might have more rows than columns due to over-determined system
    # We only need the first n equations where n = number of columns in R
    n_cols = len(R[0]) if R else 0
    Qt_b_reduced = Qt_b[:n_cols]  # Take only first n elements
    
    # Create R_square by taking only first n rows of R
    R_square = R[:n_cols]
    
    # Solve R * x = Q^T * b using back substitution
    return back_substitution(R_square, Qt_b_reduced)

def matrix_rank(A: Matrix, tol: float = 1e-12) -> int:
    """
    Compute the rank of a matrix using QR decomposition.
    """
    if not A or not A[0]:
        return 0
    
    _, R = qr_decomposition(A)
    
    rank = 0
    min_dim = min(len(R), len(R[0]))
    
    for i in range(min_dim):
        if abs(R[i][i]) > tol:
            rank += 1
    
    return rank

def condition_number(A: Matrix) -> float:
    """
    Estimate condition number of a matrix (simplified version).
    Returns ratio of largest to smallest diagonal element in R.
    """
    if not A or not A[0]:
        return float('inf')
    
    _, R = qr_decomposition(A)
    
    min_dim = min(len(R), len(R[0]))
    diag_elements = [abs(R[i][i]) for i in range(min_dim) if abs(R[i][i]) > 1e-12]
    
    if not diag_elements:
        return float('inf')
    
    return max(diag_elements) / min(diag_elements)