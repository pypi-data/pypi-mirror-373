#!/usr/bin/env python3
"""
Integration test for rthon package with C extension.
This script verifies that the C extension is working correctly.
"""

def test_rthon_integration():
    """Test rthon package integration and C extension functionality."""
    print("=== RTHON C EXTENSION INTEGRATION TEST ===\n")
    
    try:
        # Test import
        import rthon
        print("✅ rthon package imported successfully")
        
        # Check implementation info
        info = rthon.lm_info()
        print(f"✅ Implementation: {info['implementation']}")
        print(f"   Module: {info['module']}")
        print(f"   Available: {info['available']}")
        if 'performance' in info:
            print(f"   Performance: {info['performance']}")
        print()
        
        # Test C extension with perfect linear data
        print("Testing C extension with perfect linear relationship...")
        print("Expected: y = 0.5 + 1.5*x (intercept=0.5, slope=1.5)")
        
        X = [[1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6]]
        y = [2.0, 3.5, 5.0, 6.5, 8.0, 9.5]
        
        model = rthon.lm(X, y)
        print(f"✅ Model fitted successfully")
        print(f"   Type: {type(model).__name__}")
        print(f"   Coefficients: {model.coefficients}")
        print(f"   Column names: {model.column_names}")
        print(f"   R-squared: {model.r_squared:.10f}")
        print(f"   Residual std error: {model.sigma:.10f}")
        print()
        
        # Verify mathematical accuracy
        expected_intercept = 0.5
        expected_slope = 1.5
        actual_intercept, actual_slope = model.coefficients
        
        intercept_error = abs(actual_intercept - expected_intercept)
        slope_error = abs(actual_slope - expected_slope)
        r_squared_error = abs(model.r_squared - 1.0)
        
        print("Mathematical accuracy verification:")
        print(f"   Intercept error: {intercept_error:.2e}")
        print(f"   Slope error: {slope_error:.2e}")
        print(f"   R-squared error: {r_squared_error:.2e}")
        print()
        
        # Check accuracy thresholds
        if intercept_error < 1e-10 and slope_error < 1e-10 and r_squared_error < 1e-10:
            print("✅ Mathematical accuracy: EXCELLENT (< 1e-10 error)")
        elif intercept_error < 1e-6 and slope_error < 1e-6 and r_squared_error < 1e-6:
            print("✅ Mathematical accuracy: GOOD (< 1e-6 error)")
        else:
            print("❌ Mathematical accuracy: POOR (> 1e-6 error)")
            return False
        
        # Test model summary
        print("Testing model summary...")
        summary = model.summary()
        summary_lines = summary.split('\n')
        print(f"✅ Summary generated ({len(summary_lines)} lines)")
        print("   First few lines:")
        for line in summary_lines[:3]:
            print(f"     {line}")
        print()
        
        # Test predictions
        print("Testing predictions...")
        X_test = [[1, 7], [1, 8]]  # Test with x=7,8
        expected_predictions = [11.0, 12.5]  # 0.5 + 1.5*7, 0.5 + 1.5*8
        
        predictions = model.predict(X_test)
        print(f"   Test input: {X_test}")
        print(f"   Expected: {expected_predictions}")
        print(f"   Actual: {predictions}")
        
        pred_errors = [abs(pred - exp) for pred, exp in zip(predictions, expected_predictions)]
        max_pred_error = max(pred_errors)
        print(f"   Max prediction error: {max_pred_error:.2e}")
        
        if max_pred_error < 1e-10:
            print("✅ Prediction accuracy: EXCELLENT")
        else:
            print("❌ Prediction accuracy: POOR")
            return False
        
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The rthon C extension is working perfectly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   The C extension may not be built. Try:")
        print("   python setup.py build_ext --inplace")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    import os
    
    # Add src to path for development testing
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if os.path.exists(src_path):
        sys.path.insert(0, src_path)
    
    success = test_rthon_integration()
    sys.exit(0 if success else 1)