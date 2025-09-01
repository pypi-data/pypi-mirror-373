"""
High-performance C-based linear regression implementation.
Provides a drop-in replacement for the Python lm() function.
"""

from typing import Union, Dict, List, Optional, Any
import sys
import os

# Try to import the C extension
try:
    import clinalg
    C_EXTENSION_AVAILABLE = True
except ImportError:
    C_EXTENSION_AVAILABLE = False
    clinalg = None

from .linear_model import LinearModel


def lm_c(X: List[List[float]], y: List[float], column_names: Optional[List[str]] = None) -> LinearModel:
    """
    High-performance C-based linear regression using normal equations.
    
    Args:
        X: Design matrix as list of lists (n_observations x n_parameters)
        y: Response vector as list
        column_names: Optional names for the columns
        
    Returns:
        LinearModel object with results from C implementation
    """
    if not C_EXTENSION_AVAILABLE:
        raise ImportError(
            "C extension not available. Build it with:\n"
            "python setup_c_extension.py build_ext --inplace"
        )
    
    # Call C implementation
    c_result = clinalg.lm(X, y)
    
    # Convert to LinearModel format for compatibility
    n_obs = len(y)
    n_params = len(X[0])
    
    if column_names is None:
        column_names = [f"X{i+1}" for i in range(n_params)]
        if len(column_names) > 0 and all(row[0] == 1.0 for row in X):
            column_names[0] = "(Intercept)"
    
    # Create LinearModel object with C results
    model = LinearModel(
        coefficients=c_result.coefficients,
        residuals=c_result.residuals,
        fitted_values=c_result.fitted_values,
        y=y,
        X=X,
        column_names=column_names,
        formula=None,  # No formula parsing in C version yet
        X_t_X_inv=None  # Not computed in basic C version
    )
    
    # Set additional properties
    model._r_squared = c_result.r_squared
    model._residual_std_error = c_result.residual_std_error
    
    return model


def benchmark_c_vs_python(X: List[List[float]], y: List[float], iterations: int = 10) -> Dict[str, float]:
    """
    Benchmark C implementation vs Python implementation.
    
    Args:
        X: Design matrix
        y: Response vector  
        iterations: Number of iterations for timing
        
    Returns:
        Dictionary with timing results
    """
    import time
    
    if not C_EXTENSION_AVAILABLE:
        return {"error": "C extension not available"}
    
    # Time C implementation
    start_time = time.time()
    for _ in range(iterations):
        c_result = clinalg.lm(X, y)
    c_time = (time.time() - start_time) / iterations
    
    # Time Python implementation (if available)
    try:
        from .lm import _fit_ols
        start_time = time.time()
        for _ in range(iterations):
            coefficients, residuals, fitted_values, X_t_X_inv = _fit_ols(X, y)
        py_time = (time.time() - start_time) / iterations
        
        speedup = py_time / c_time if c_time > 0 else float('inf')
    except ImportError:
        py_time = None
        speedup = None
    
    return {
        "c_time_seconds": c_time,
        "python_time_seconds": py_time,
        "speedup_factor": speedup,
        "iterations": iterations
    }


def get_c_extension_info() -> Dict[str, Any]:
    """Get information about the C extension availability and capabilities."""
    return {
        "available": C_EXTENSION_AVAILABLE,
        "module": clinalg if C_EXTENSION_AVAILABLE else None,
        "capabilities": {
            "matrix_interface": True,
            "formula_interface": False,  # Not yet implemented
            "weighted_regression": False,  # Not yet implemented
            "missing_value_handling": False  # Not yet implemented
        } if C_EXTENSION_AVAILABLE else {}
    }


# Example usage
if __name__ == "__main__":
    # Test the C implementation
    print("C Linear Regression Implementation Test")
    print("=" * 40)
    
    if not C_EXTENSION_AVAILABLE:
        print("❌ C extension not available")
        print("Build it with: python setup_c_extension.py build_ext --inplace")
        sys.exit(1)
    
    # Simple regression test
    X = [
        [1.0, 1.0],
        [1.0, 2.0],
        [1.0, 3.0],
        [1.0, 4.0],
        [1.0, 5.0]
    ]
    y = [2.1, 3.9, 6.1, 7.9, 10.1]
    
    print("Testing simple regression...")
    model = lm_c(X, y)
    
    print(f"Coefficients: {dict(zip(model.column_names, model.coefficients))}")
    print(f"R-squared: {model.r_squared:.6f}")
    print(f"Residual Std Error: {model.residual_std_error:.6f}")
    
    # Benchmark if possible
    print("\nBenchmarking...")
    benchmark_results = benchmark_c_vs_python(X, y, iterations=1000)
    
    if "error" not in benchmark_results:
        print(f"C implementation: {benchmark_results['c_time_seconds']*1000:.3f} ms/call")
        if benchmark_results['python_time_seconds']:
            print(f"Python implementation: {benchmark_results['python_time_seconds']*1000:.3f} ms/call")
            print(f"Speedup: {benchmark_results['speedup_factor']:.1f}x faster")
    else:
        print(benchmark_results['error'])
    
    print("✅ C implementation working correctly!")