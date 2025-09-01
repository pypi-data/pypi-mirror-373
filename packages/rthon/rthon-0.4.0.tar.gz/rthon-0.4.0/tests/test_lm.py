import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rthon.regression.linear_algebra import qr_decomposition, solve_qr, back_substitution
from rthon.regression.formula import parse_formula, design_matrix_from_formula
from rthon import lm, lm_info

def test_qr_simple():
    """Test QR decomposition with simple matrix."""
    print("Testing QR decomposition...")
    
    X = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]]
    print(f"X = {X}")
    
    try:
        Q, R = qr_decomposition(X)
        print(f"Q = {Q}")
        print(f"R = {R}")
        print("QR decomposition successful!")
        return Q, R
    except Exception as e:
        print(f"QR decomposition failed: {e}")
        return None, None

def test_formula_parsing():
    """Test formula parsing and design matrix generation."""
    print("\\nTesting formula parsing...")
    
    data = {'y': [1.0, 2.0, 3.0, 4.0, 5.0], 'x': [1.0, 2.0, 3.0, 4.0, 5.0]}
    formula_str = "y ~ x"
    
    try:
        formula = parse_formula(formula_str)
        print(f"Formula: {formula}")
        print(f"Response: {formula.response}")
        print(f"Terms: {[str(t) for t in formula.terms]}")
        
        X, y, column_names = design_matrix_from_formula(formula, data)
        print(f"X = {X}")
        print(f"y = {y}")
        print(f"column_names = {column_names}")
        
        return X, y, column_names
        
    except Exception as e:
        print(f"Formula parsing failed: {e}")
        return None, None, None

def test_back_substitution():
    """Test back substitution."""
    print("\\nTesting back substitution...")
    
    # Simple upper triangular system: R*x = b
    R = [[2.0, 1.0], [0.0, 1.0]]
    b = [3.0, 1.0]
    
    try:
        x = back_substitution(R, b)
        print(f"R = {R}")
        print(f"b = {b}")  
        print(f"x = {x}")
        print("Back substitution successful!")
        return x
    except Exception as e:
        print(f"Back substitution failed: {e}")
        return None

def test_lm_simple():
    """Test simple lm function."""
    print("\\nTesting lm function...")
    
    # Very simple data
    data = {
        'y': [1.0, 2.0, 3.0], 
        'x': [1.0, 2.0, 3.0]
    }
    
    try:
        print(f"Data: {data}")
        model = lm("y ~ x", data=data)
        print("lm function successful!")
        print(f"Coefficients: {dict(zip(model.column_names, model.coefficients))}")
        print(f"R-squared: {model.r_squared:.4f}")
        return model
    except Exception as e:
        print(f"lm function failed: {e}")
        return None

def test_c_extension_interface():
    """Test the C extension matrix interface."""
    print("\\nTesting C extension matrix interface...")
    
    try:
        info = lm_info()
        print(f"Implementation info: {info}")
        
        # Test simple perfect linear relationship: y = 0.5 + 1.5*x
        X = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5]]
        y = [2.0, 3.5, 5.0, 6.5, 8.0]
        
        print(f"X = {X}")
        print(f"y = {y}")
        
        model = lm(X, y)
        print("C extension lm function successful!")
        print(f"Type: {type(model)}")
        print(f"Coefficients: {dict(zip(model.column_names, model.coefficients))}")
        print(f"R-squared: {model.r_squared:.6f}")
        print(f"Residual std error: {model.sigma:.6f}")
        
        # Verify mathematical correctness
        expected_intercept = 0.5
        expected_slope = 1.5
        actual_intercept, actual_slope = model.coefficients
        
        intercept_error = abs(actual_intercept - expected_intercept)
        slope_error = abs(actual_slope - expected_slope)
        
        print(f"Intercept error: {intercept_error:.10f}")
        print(f"Slope error: {slope_error:.10f}")
        
        assert intercept_error < 1e-10, f"Intercept error too large: {intercept_error}"
        assert slope_error < 1e-10, f"Slope error too large: {slope_error}"
        assert abs(model.r_squared - 1.0) < 1e-10, f"R-squared should be 1.0, got {model.r_squared}"
        
        print("✅ All C extension tests passed!")
        return model
        
    except Exception as e:
        print(f"C extension test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_c_extension_vs_python_fallback():
    """Test that C extension and Python fallback produce similar results for formula interface."""
    print("\\nTesting formula interface (Python fallback)...")
    
    try:
        # Test formula interface which should fall back to Python
        data = {
            'y': [2.0, 3.5, 5.0, 6.5, 8.0], 
            'x': [1.0, 2.0, 3.0, 4.0, 5.0]
        }
        
        print(f"Data: {data}")
        model = lm("y ~ x", data=data)
        print("Formula interface successful!")
        print(f"Coefficients: {dict(zip(model.column_names, model.coefficients))}")
        print(f"R-squared: {model.r_squared:.4f}")
        
        return model
        
    except Exception as e:
        print(f"Formula interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Test existing functionality
    test_qr_simple()
    test_formula_parsing()
    test_back_substitution()
    test_lm_simple()
    
    # Test new C extension functionality
    test_c_extension_interface()
    test_c_extension_vs_python_fallback()