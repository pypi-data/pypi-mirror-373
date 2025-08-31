"""Output utilities for controlling verbosity."""

import os
import sys


def debug_print(*args, **kwargs):
    """Print only if debug mode is enabled."""
    if os.environ.get("NETINTEL_OCR_DEBUG", "0") == "1":
        print(*args, **kwargs)


def info_print(*args, **kwargs):
    """Print unless quiet mode is enabled."""
    if os.environ.get("NETINTEL_OCR_QUIET", "0") != "1":
        print(*args, **kwargs)


def always_print(*args, **kwargs):
    """Always print (for essential output like final path)."""
    print(*args, **kwargs)


def progress_print(*args, **kwargs):
    """Print progress unless quiet mode."""
    if os.environ.get("NETINTEL_OCR_QUIET", "0") != "1":
        # Print without newline for progress updates
        print(*args, **kwargs, end='', flush=True)


class ConditionalPrinter:
    """Context manager for conditional output."""
    
    def __init__(self):
        self.debug_mode = os.environ.get("NETINTEL_OCR_DEBUG", "0") == "1"
        self.quiet_mode = os.environ.get("NETINTEL_OCR_QUIET", "0") == "1"
    
    def debug(self, message):
        """Debug level output."""
        if self.debug_mode:
            print(f"[DEBUG] {message}")
    
    def info(self, message):
        """Info level output."""
        if not self.quiet_mode:
            print(message)
    
    def progress(self, message, end='\n'):
        """Progress updates."""
        if not self.quiet_mode:
            print(message, end=end, flush=True)
    
    def success(self, message):
        """Success messages."""
        if not self.quiet_mode:
            print(f"✓ {message}")
    
    def warning(self, message):
        """Warning messages (shown unless quiet)."""
        if not self.quiet_mode:
            print(f"⚠ {message}")
    
    def error(self, message):
        """Error messages (always shown)."""
        print(f"✗ {message}", file=sys.stderr)
    
    def result(self, message):
        """Final result (always shown)."""
        print(message)


# Global printer instance
printer = ConditionalPrinter()