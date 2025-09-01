"""
Build script for C++ deduplication core
This is invoked by the main setup.py during pip install
"""

from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import pybind11
import platform
import os

# Detect platform capabilities
def has_avx2():
    """Check if CPU supports AVX2 instructions."""
    if platform.machine() not in ['x86_64', 'AMD64']:
        return False
    
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        return 'avx2' in info.get('flags', [])
    except:
        # Fallback: assume AVX2 on modern x86_64
        return True

def has_openmp():
    """Check if OpenMP is available."""
    return platform.system() != 'Windows'  # OpenMP is complex on Windows

# Define C++ extension
cpp_args = ['-O3', '-std=c++14']
link_args = []

if platform.system() == 'Darwin':  # macOS
    cpp_args.extend(['-stdlib=libc++', '-mmacosx-version-min=10.14'])
    if has_openmp():
        cpp_args.append('-Xpreprocessor')
        cpp_args.append('-fopenmp')
        link_args.extend(['-lomp'])
elif platform.system() == 'Linux':
    if has_openmp():
        cpp_args.append('-fopenmp')
        link_args.append('-fopenmp')
    if has_avx2():
        cpp_args.append('-mavx2')

ext_modules = [
    Pybind11Extension(
        "dedup_core",
        sources=[
            "dedup_cpp/simhash.cpp",
            "dedup_cpp/cdc.cpp",
            "python_bindings.cpp"
        ],
        include_dirs=[
            pybind11.get_include(),
            "dedup_cpp"
        ],
        cxx_std=14,
        extra_compile_args=cpp_args,
        extra_link_args=link_args,
    ),
]

setup(
    name="netintel_ocr_dedup_core",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)