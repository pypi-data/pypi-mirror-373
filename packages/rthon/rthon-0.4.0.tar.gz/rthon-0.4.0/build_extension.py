#!/usr/bin/env python3
"""
Build script for rthon C extension.
Provides better error handling and user feedback than setup.py.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required build dependencies are available."""
    print("🔍 Checking build dependencies...")
    
    try:
        import numpy
        print(f"✅ NumPy found: {numpy.__version__}")
        numpy_include = numpy.get_include()
        print(f"   Include path: {numpy_include}")
    except ImportError:
        print("❌ NumPy not found. Install with: pip install numpy")
        return False
    
    # Check for compiler
    try:
        result = subprocess.run(['gcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            gcc_version = result.stdout.split('\n')[0]
            print(f"✅ GCC found: {gcc_version}")
        else:
            print("❌ GCC not available")
            return False
    except FileNotFoundError:
        print("❌ GCC not found. Install build tools for your platform.")
        return False
    
    return True

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    patterns_to_remove = [
        "build/",
        "dist/",
        "src/**/*.so",
        "src/**/__pycache__/",
        "**/*.egg-info/",
    ]
    
    removed_count = 0
    for pattern in patterns_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
                removed_count += 1
            elif path.is_file():
                path.unlink()
                print(f"   Removed file: {path}")
                removed_count += 1
    
    if removed_count == 0:
        print("   No artifacts to clean")
    else:
        print(f"   Cleaned {removed_count} items")

def build_extension():
    """Build the C extension."""
    print("🔨 Building C extension...")
    
    try:
        # Use the setup.py build command
        cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']
        print(f"   Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ C extension built successfully")
            
            # Find the built extension
            for so_file in Path('src').rglob('*.so'):
                print(f"   Created: {so_file}")
            
            return True
        else:
            print("❌ Build failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def test_extension():
    """Test the built extension."""
    print("🧪 Testing built extension...")
    
    try:
        # Add src to Python path
        sys.path.insert(0, 'src')
        
        # Try to import and test
        import rthon
        info = rthon.lm_info()
        
        if info['available'] and 'C' in info['implementation']:
            print("✅ C extension is working")
            print(f"   Implementation: {info['implementation']}")
            print(f"   Module: {info['module']}")
            
            # Quick functionality test
            X = [[1, 1], [1, 2], [1, 3]]
            y = [2, 4, 6]
            model = rthon.lm(X, y)
            
            expected_slope = 2.0
            actual_slope = model.coefficients[1]
            error = abs(actual_slope - expected_slope)
            
            if error < 1e-10:
                print("✅ Functionality test passed")
                return True
            else:
                print(f"❌ Functionality test failed: slope error {error}")
                return False
        else:
            print("❌ C extension not available")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main build process."""
    print("🚀 Building rthon C extension\n")
    
    if not check_dependencies():
        print("\n❌ Build failed: Missing dependencies")
        return 1
    
    print()
    clean_build()
    
    print()
    if not build_extension():
        print("\n❌ Build failed: Compilation error")
        return 1
    
    print()
    if not test_extension():
        print("\n❌ Build failed: Extension test failed")
        return 1
    
    print("\n🎉 Build completed successfully!")
    print("The rthon package is ready to use with high-performance C linear regression.")
    print("\nTry it out:")
    print("  python -c \"import rthon; print(rthon.lm_info())\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())