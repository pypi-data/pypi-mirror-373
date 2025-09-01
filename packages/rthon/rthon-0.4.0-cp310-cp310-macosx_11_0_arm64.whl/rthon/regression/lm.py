"""
Implementation of R's lm() function for linear regression.
Main entry point for linear modeling functionality.
"""

from __future__ import annotations
from typing import Union, Dict, List, Optional, Any

from .linear_algebra import (
    Matrix, Vector, qr_decomposition, solve_qr, matrix_multiply, 
    transpose, matrix_vector_multiply, matrix_rank
)
from .formula import Formula, design_matrix_from_formula, parse_formula
from .linear_model import LinearModel

def lm(formula: Union[str, Formula, Matrix, Vector], 
       data: Optional[Union[Dict[str, Vector], Matrix]] = None,
       y: Optional[Vector] = None,
       subset: Optional[List[int]] = None,
       weights: Optional[Vector] = None,
       na_action: str = "omit") -> LinearModel:
    """
    Fit a linear model using least squares regression.
    
    This function replicates R's lm() functionality with multiple input formats:
    
    1. Formula interface: lm("y ~ x1 + x2", data=data_dict)
    2. Matrix interface: lm(X, y=y_vector)
    3. Arrays: lm([X_matrix], [y_vector])
    
    Args:
        formula: Formula string, Formula object, or design matrix X
        data: Data dictionary (variable_name -> values) or design matrix
        y: Response vector (when using matrix interface)
        subset: Row indices to include (not implemented yet)
        weights: Observation weights (not implemented yet)
        na_action: How to handle missing values (not implemented yet)
    
    Returns:
        LinearModel object with fitted regression results
        
    Examples:
        # Formula interface
        model = lm("mpg ~ hp + wt", data={"mpg": [21, 22, 18], "hp": [110, 95, 150], "wt": [2.5, 2.3, 3.2]})
        
        # Matrix interface
        X = [[1, 110, 2.5], [1, 95, 2.3], [1, 150, 3.2]]  # Including intercept
        y = [21, 22, 18]
        model = lm(X, y=y)
        
        # Alternative matrix format
        model = lm(X, y)
    """
    
    # Parse inputs and create design matrix
    X, y_vec, column_names, formula_obj = _parse_inputs(formula, data, y)
    
    # Validate inputs
    if not X or not y_vec:
        raise ValueError("No data provided")
    
    if len(X) != len(y_vec):
        raise ValueError(f"Number of observations in X ({len(X)}) doesn't match y ({len(y_vec)})")
    
    if not X[0]:
        raise ValueError("Design matrix X is empty")
    
    n = len(X)  # Number of observations
    p = len(X[0])  # Number of parameters
    
    if n <= p:
        raise ValueError(f"Not enough observations ({n}) for {p} parameters")
    
    # Check for rank deficiency
    rank = matrix_rank(X)
    if rank < p:
        raise ValueError(f"Design matrix is rank deficient (rank={rank}, p={p}). Perfect multicollinearity detected.")
    
    # Fit the model using QR decomposition
    try:
        coefficients, residuals, fitted_values, X_t_X_inv = _fit_ols(X, y_vec)
    except Exception as e:
        raise ValueError(f"Failed to fit model: {str(e)}")
    
    # Create and return LinearModel object
    model = LinearModel(
        coefficients=coefficients,
        residuals=residuals,
        fitted_values=fitted_values,
        y=y_vec,
        X=X,
        column_names=column_names,
        formula=formula_obj,
        X_t_X_inv=X_t_X_inv
    )
    
    return model

def _parse_inputs(formula: Union[str, Formula, Matrix, Vector], 
                 data: Optional[Union[Dict[str, Vector], Matrix]], 
                 y: Optional[Vector]) -> tuple[Matrix, Vector, List[str], Optional[Formula]]:
    """
    Parse different input formats into standardized X, y, column_names, formula.
    """
    
    # Case 1: Formula interface
    if isinstance(formula, (str, Formula)):
        if data is None:
            raise ValueError("Data dictionary required when using formula interface")
        
        if isinstance(data, dict):
            # Parse formula and create design matrix
            if isinstance(formula, str):
                formula_obj = parse_formula(formula)
            else:
                formula_obj = formula
            
            X, y_vec, column_names = design_matrix_from_formula(formula_obj, data)
            return X, y_vec, column_names, formula_obj
        
        else:
            raise ValueError("Data must be a dictionary when using formulas")
    
    # Case 2: Matrix interface - lm(X, y=y_vector)
    elif isinstance(formula, list) and y is not None:
        X = formula
        y_vec = y
        
        # Validate matrix format
        if not all(isinstance(row, list) and len(row) == len(X[0]) for row in X):
            raise ValueError("X must be a matrix (list of lists with equal length)")
        
        # Generate column names
        p = len(X[0])
        column_names = [f"X{i+1}" for i in range(p)]
        
        # Check if first column is all ones (intercept)
        if all(row[0] == 1.0 for row in X):
            column_names[0] = "(Intercept)"
        
        return X, y_vec, column_names, None
    
    # Case 3: Alternative matrix format - lm(X, y) where second argument is y
    elif isinstance(formula, list) and isinstance(data, list) and y is None:
        X = formula
        y_vec = data
        
        # Validate matrix format
        if not all(isinstance(row, list) and len(row) == len(X[0]) for row in X):
            raise ValueError("X must be a matrix (list of lists with equal length)")
        
        # Generate column names
        p = len(X[0])
        column_names = [f"X{i+1}" for i in range(p)]
        
        # Check if first column is all ones (intercept)
        if all(row[0] == 1.0 for row in X):
            column_names[0] = "(Intercept)"
        
        return X, y_vec, column_names, None
    
    else:
        raise ValueError("Invalid input format. Use either formula interface or matrix interface.")

def _fit_ols(X: Matrix, y: Vector) -> tuple[Vector, Vector, Vector, Matrix]:
    """
    Fit ordinary least squares using QR decomposition.
    
    Returns:
        coefficients: Estimated coefficients (beta_hat)
        residuals: y - y_hat  
        fitted_values: X * beta_hat
        X_t_X_inv: (X'X)^(-1) for standard errors
    """
    try:
        # QR decomposition of X
        Q, R = qr_decomposition(X)
        
        # Solve for coefficients: R * beta = Q^T * y
        coefficients = solve_qr(Q, R, y)
        
        # Calculate fitted values: y_hat = X * beta
        fitted_values = matrix_vector_multiply(X, coefficients)
        
        # Calculate residuals: e = y - y_hat
        residuals = [y[i] - fitted_values[i] for i in range(len(y))]
        
        # Calculate (X'X)^(-1) for standard errors
        # (X'X)^(-1) = (R'R)^(-1) = R^(-1) * R'^(-1)
        X_t_X_inv = _compute_xtx_inverse(R)
        
        return coefficients, residuals, fitted_values, X_t_X_inv
        
    except Exception as e:
        raise ValueError(f"QR decomposition failed: {str(e)}")

def _compute_xtx_inverse(R: Matrix) -> Matrix:
    """
    Compute (X'X)^(-1) = R^(-1) * R'^(-1) from QR decomposition.
    This is a simplified implementation.
    """
    p = len(R)
    if p == 0:
        return []
    
    # Create identity matrix
    inv_R = [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
    
    # Back substitution to compute R^(-1) (simplified)
    for i in range(p):
        # Solve R * col_i = e_i for each column of R^(-1)
        try:
            for k in range(p-1, -1, -1):
                if abs(R[k][k]) < 1e-12:
                    # Singular matrix
                    inv_R[k][i] = 0.0
                    continue
                    
                inv_R[k][i] /= R[k][k]
                for j in range(k):
                    inv_R[j][i] -= R[j][k] * inv_R[k][i]
        except:
            # If computation fails, use identity as fallback
            inv_R = [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
            break
    
    # Compute R^(-1) * R'^(-1) = (X'X)^(-1)
    try:
        R_inv_t = transpose(inv_R)
        X_t_X_inv = matrix_multiply(inv_R, R_inv_t)
    except:
        # Fallback to identity
        X_t_X_inv = [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]
    
    return X_t_X_inv

# Convenience functions
def summary_lm(model: LinearModel) -> str:
    """Print summary of linear model."""
    return model.summary()

def predict_lm(model: LinearModel, newdata: Optional[Matrix] = None, 
               interval: str = "none", level: float = 0.95):
    """Predict using linear model."""
    return model.predict(newdata, interval, level)

def residuals_lm(model: LinearModel) -> Vector:
    """Extract residuals from linear model."""
    return model.residuals_method()

def fitted_lm(model: LinearModel) -> Vector:
    """Extract fitted values from linear model."""
    return model.fitted()

# Example usage
def example_usage():
    """Example usage of lm() function."""
    
    # Example 1: Formula interface
    print("Example 1: Formula interface")
    data = {
        "mpg": [21.0, 21.0, 22.8, 21.4, 18.7, 18.1, 14.3, 24.4, 22.8, 19.2],
        "hp": [110, 110, 93, 110, 175, 105, 245, 62, 95, 123],
        "wt": [2.620, 2.875, 2.320, 3.215, 3.440, 3.460, 3.570, 3.190, 3.150, 3.440]
    }
    
    try:
        model1 = lm("mpg ~ hp + wt", data=data)
        print("Formula model fitted successfully")
        print(f"Coefficients: {dict(zip(model1.column_names, model1.coefficients))}")
        print(f"R-squared: {model1.r_squared:.4f}")
        print()
    except Exception as e:
        print(f"Error in formula model: {e}")
    
    # Example 2: Matrix interface
    print("Example 2: Matrix interface")
    X = [[1, 110, 2.620], [1, 110, 2.875], [1, 93, 2.320], [1, 110, 3.215], [1, 175, 3.440]]
    y = [21.0, 21.0, 22.8, 21.4, 18.7]
    
    try:
        model2 = lm(X, y=y)
        print("Matrix model fitted successfully")
        print(f"Coefficients: {dict(zip(model2.column_names, model2.coefficients))}")
        print(f"R-squared: {model2.r_squared:.4f}")
    except Exception as e:
        print(f"Error in matrix model: {e}")

if __name__ == "__main__":
    example_usage()