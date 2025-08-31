"""
NetIntel-OCR Version Information with C++ Core Detection
"""

import json
import subprocess
import sys
from typing import Dict, Any, Optional

__version__ = "0.1.15.2"
__cpp_core_version__ = "1.0.0"

def check_cpp_core() -> bool:
    """Check if C++ deduplication core is available."""
    try:
        from text_dedup import SimHash, CDC, AVAILABLE
        return AVAILABLE
    except ImportError:
        return False

def check_faiss() -> Optional[str]:
    """Check if Faiss is available and return version."""
    try:
        import faiss
        return faiss.__version__
    except ImportError:
        return None

def check_avx2() -> bool:
    """Check if AVX2 instructions are available."""
    try:
        import platform
        if platform.machine() in ['x86_64', 'AMD64']:
            # Check CPU flags on Linux
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'avx2' in cpuinfo.lower()
    except:
        pass
    return False

def check_openmp() -> bool:
    """Check if OpenMP is available."""
    try:
        # Try to import the C++ core which uses OpenMP
        from text_dedup import _openmp_available
        return _openmp_available()
    except:
        return False

def get_version_info() -> Dict[str, Any]:
    """Get comprehensive version information."""
    return {
        "version": __version__,
        "cpp_core": check_cpp_core(),
        "cpp_core_version": __cpp_core_version__ if check_cpp_core() else None,
        "faiss": check_faiss(),
        "avx2": check_avx2(),
        "openmp": check_openmp(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

def format_version_string(json_format: bool = False) -> str:
    """Format version information for display."""
    info = get_version_info()
    
    if json_format:
        return json.dumps(info, indent=2)
    
    # Build human-readable string
    parts = [f"NetIntel-OCR v{info['version']}"]
    
    if info['cpp_core']:
        parts.append(f"C++ Core: v{info['cpp_core_version']}")
    else:
        parts.append("C++ Core: Disabled (Python fallback)")
    
    if info['faiss']:
        parts.append(f"Faiss: {info['faiss']}")
    
    if info['avx2']:
        parts.append("AVX2: ✓")
    
    if info['openmp']:
        parts.append("OpenMP: ✓")
    
    return f"{parts[0]} ({', '.join(parts[1:])})"