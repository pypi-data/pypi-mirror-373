"""
NetIntel-OCR Text Deduplication Module with C++ Core or Python Fallback
"""

try:
    # Try to import C++ core
    from .dedup_core import SimHash, CDC, _openmp_available, has_avx2, has_openmp, __version__
    AVAILABLE = True
except ImportError:
    # Fall back to Python implementation
    try:
        from .fallback import SimHash, CDC, _openmp_available, has_avx2, has_openmp, __version__
        AVAILABLE = False  # C++ not available, but Python fallback is
    except ImportError:
        # No fallback available either
        AVAILABLE = False
        SimHash = None
        CDC = None
        _openmp_available = lambda: False
        has_avx2 = lambda: False
        has_openmp = lambda: False
        __version__ = "0.0.0"

__all__ = ['SimHash', 'CDC', '_openmp_available', 'has_avx2', 'has_openmp', '__version__', 'AVAILABLE']