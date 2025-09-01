"""
Setup script for rthon package with C extensions.
This works alongside pyproject.toml to handle C compilation.
"""

from setuptools import setup, Extension, find_packages
import sys
import os

try:
    import numpy
    numpy_include = numpy.get_include()
except ImportError:
    # Fallback for build environments where numpy isn't installed yet
    numpy_include = []

# Define the C extension module
regression_c_ext = Extension(
    'rthon.regression._c_ext',
    sources=[
        'src/rthon/regression/_c_ext/python_lm.c',
        'src/rthon/regression/_c_ext/matrix.c'
    ],
    include_dirs=[
        'src/rthon/regression/_c_ext',
        numpy_include
    ],
    extra_compile_args=['-O3', '-std=c99'],
    extra_link_args=['-lm'],
    depends=[
        'src/rthon/regression/_c_ext/python_lm.h',
        'src/rthon/regression/_c_ext/matrix.h'
    ]
)

# Check if we're in a build environment that can compile C extensions
can_build_c_extensions = True
try:
    # Try to detect if we have the necessary build tools
    import distutils.util
    import distutils.ccompiler
    compiler = distutils.ccompiler.new_compiler()
    if compiler is None:
        can_build_c_extensions = False
except Exception:
    can_build_c_extensions = False

# Only include C extension if we can build it
ext_modules = []
if can_build_c_extensions:
    ext_modules = [regression_c_ext]
    print("✅ Will build C extension for high-performance linear regression")
else:
    print("⚠️  C extension build not available - will use Python fallback")

setup(
    # Basic package info is in pyproject.toml
    # This setup.py only handles the C extension
    ext_modules=ext_modules,
    zip_safe=False,
    
    # Ensure numpy is available for C compilation
    setup_requires=['numpy'],
)