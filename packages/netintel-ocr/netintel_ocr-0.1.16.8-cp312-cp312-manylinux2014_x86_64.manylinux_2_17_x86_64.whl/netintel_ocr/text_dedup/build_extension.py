#!/usr/bin/env python
"""Build C++ extension for text_dedup module."""

import os
import sys
import subprocess
from pathlib import Path

def build_cpp_extension():
    """Build the C++ extension if not already built."""
    current_dir = Path(__file__).parent
    
    # Check if .so file already exists
    so_files = list(current_dir.glob("*.so"))
    if so_files:
        print(f"C++ extension already built: {so_files[0].name}")
        return True
    
    # Try to build the extension
    try:
        # Check if we have the required build tools
        subprocess.run(["g++", "--version"], capture_output=True, check=True)
        
        # Build using setup.py
        setup_py = current_dir / "setup.py"
        if setup_py.exists():
            print("Building C++ extension for text_dedup...")
            result = subprocess.run(
                [sys.executable, "setup.py", "build_ext", "--inplace"],
                cwd=str(current_dir),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("C++ extension built successfully!")
                return True
            else:
                print(f"Warning: C++ extension build failed: {result.stderr}")
                print("Falling back to Python implementation")
                return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"C++ build tools not available: {e}")
        print("Using Python fallback implementation")
        return False

if __name__ == "__main__":
    build_cpp_extension()